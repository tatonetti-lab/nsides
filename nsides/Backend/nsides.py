"""
NSIDES

The nSides web front-end, (re)implemented in Flask

@author: Joseph D. Romano
@author: Rami Vanguri
@author: Choonhan Youn

(c) 2017 Tatonetti Lab

"""

import os
from flask import Flask, request, session, redirect, url_for, render_template, flash, jsonify, make_response, send_from_directory
from flask_cors import CORS
# from urlparse import urlparse, urljoin
# from werkzeug.security import generate_password_hash
import query_nsides_mongo
import query_nsides_mysql
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from functools import wraps
import requests
import click
import json
from datetime import datetime
from oauth2client.client import flow_from_clientsecrets
from pprint import pprint
from nsides_helpers import convertDrugsToIngredients
# response is automatically created for each app.route

def authenticated(fn):
    """Decorator for requiring authentication on a route."""
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        print 'Authentication triggered'
        if not session.get('is_authenticated'):
            return redirect(url_for('login', next=request.url))
        if request.path == '/logout':
            return fn(*args, **kwargs)
        return fn(*args, **kwargs)
    return decorated_function

#########
# INITS #
#########

app = Flask(__name__, template_folder='../Frontend/dist', static_folder='../Frontend/dist')
CORS(app)
app.secret_key = 'changeme'
#app.config.from_envvar('NSIDES_FRONTEND_SETTINGS', silent=True)
app.config.from_pyfile('nsides_flask.conf')

with open(app.config['JOB_TEMPLATE']) as f:
    jobtemplate = json.load(f)

MONGODB_HOST, MONGODB_UN, MONGODB_PW = open('./nsides-mongo.cnf').read().strip().split('\n')
MONGODB_PORT = 27017

class UserDb(object):
    def __init__(self):
        #self.client = MongoClient('mongodb://%s:%s@%s:%s/nsides_dev' % (MONGODB_UN, MONGODB_PW, MONGODB_HOST, MONGODB_PORT))
        self.client = MongoClient('mongodb://%s:%s@%s:%s/nsides_dev?authSource=admin' % (MONGODB_UN, MONGODB_PW, MONGODB_HOST, MONGODB_PORT))
        self.users = self.client.nsides_dev.users

    def submit_new_user(self, name, institution,
                        email, pw):
        pw_hash = generate_password_hash(pw, method='pbkdf2:sha256')
        try:
            self.users.insert_one({"_id": email, "name": name,
                                   "institution": institution, "pw_hash": pw_hash})
            return email
        except DuplicateKeyError:
            print("Error creating user - email already exists")
            return None

    def save_profile(self, identity_id=None, name=None, email=None, institution=None):
        try:
            self.users.insert_one({"_id": identity_id,
                                   "name": name,
                                   "email": email,
                                   "institution": institution})
            return email
        except DuplicateKeyError:
            print("Error creating user - already exists")
            return None

    def load_profile(self, identity_id=None):
        try:
            user = self.users.find_one({"_id": identity_id})
            return (user['name'], user['email'], user['institution'])
        except TypeError:
            return None

udb = UserDb()


###########
# HELPERS #
###########

def load_portal_client(redirect_uri):
    """Create an AuthClient for the portal"""
    flow = flow_from_clientsecrets(app.config['CLIENT_SECRET'],
                                   scope='PRODUCTION',
                                   redirect_uri=redirect_uri)
    print 'flow \n ', flow
    return flow

def get_result(base_url, path, access_token):
    req_url = '{}/{}{}'.format(base_url, path, '?pretty=true')
    print 'GET request url:',req_url
    req_headers = dict(Authorization='Bearer {}'.format(access_token))
    resp = requests.get(req_url,
                        headers=req_headers,
                        verify=False)
    # resp.raise_for_status()
    # print 'Status code:', resp.status_code
    resp_result = resp.json()
    # print 'Response:', resp_result

    if 'status' in resp_result:
        if resp_result['status'] == 'error':
            print 'error message:', resp_result['message']
            return False, resp_result['message']
    elif 'fault' in resp_result:
        return False, resp_result['fault']['message']
    else:
        return False, resp_result

    # resp.raise_for_status()
    return True, resp_result['result']

def post_result(base_url, path, access_token, data_type, post_data):
    if path is None:
        req_url = '{}{}'.format(base_url, '?pretty=true')
    else:
        req_url = '{}/{}{}'.format(base_url, path, '?pretty=true')
    # print 'POST request url:', req_url
    req_headers = dict(Authorization='Bearer {}'.format(access_token))
    print ""
    print "POST URL:"
    print req_url
    print "HEADERS:"
    # print pprint(req_headers)
    print "JSON:"
    # print pprint(post_data)
    print ""
    if data_type == 'json':
        resp = requests.post(req_url, headers=req_headers, json=post_data, verify=False)
    elif data_type == 'data':
        resp = requests.post(req_url, headers=req_headers, data=post_data, verify=False)
    else:
        resp = 'Please choose the data type: "json" or "data"'
        # print resp
        return False, resp

    # print 'Status code:', resp.status_code
    resp_result = resp.json()
    # print 'Response:', resp_result
    
    if 'status' in resp_result:
        if resp_result['status'] == 'error':
            # print 'error message:', resp_result['message']
            return False, resp_result['message']
    elif 'fault' in resp_result:
        return False, resp_result['fault']['message']
    else:
        return False, resp_result

    return True, resp_result['result']

def handle_permission(username):
    # Note: this is specific to the 'nsidescommunity' account that
    # has been registered with Agave - don't check the token into version control!
    nsides_token = app.config['NSIDESCOMMUNITY_ACCESS_TOKEN']

    # set permission for execution host to submit the job
    path = '{}/{}/{}'.format(app.config['SYSTEM_EXEC_ID'], 'roles', username)
    resp = get_result(app.config['SYSTEM_URL_BASE'],path,nsides_token)
    if not resp[0]:
        role = {"role": "USER"}
        resp = post_result(app.config['SYSTEM_URL_BASE'], path, nsides_token, 'json', role)
        print 'Result:', resp[1]
    
    # set permission for storage service
    path = '{}/{}/{}'.format(app.config['SYSTEM_STOR_ID'], 'roles', username)
    resp = get_result(app.config['SYSTEM_URL_BASE'], path, nsides_token)
    if not resp[0]:
        role = {"role": "USER"}
        resp = post_result(app.config['SYSTEM_URL_BASE'], path, nsides_token, 'json', role)
        print 'Result:', resp[1]
    
    # set permissions for application service
    path = '{}/{}/{}'.format(app.config['APP_ID'], 'pems', username)
    resp = get_result(app.config['APP_URL_BASE'], path, nsides_token)
    if not resp[0]:
        perm = 'permission=READ_EXECUTE'
        resp = post_result(app.config['APP_URL_BASE'], path, nsides_token, 'data', perm)
        print 'Result:', resp[1]

def get_job(model_type, model_index):
    j_tokens = json.loads(session['tokens'])
    jobtemplate['name'] = datetime.now().strftime("%Y-%m%d %H:%M:%S.%f")[:-3]
    jobtemplate['appId'] = app.config['APP_ID']
    jobtemplate['archiveSystem'] = app.config['SYSTEM_STOR_ID']
    archival_path = app.config['SYSTEM_STOR_PATH']
    archival_path = archival_path.replace("<username>",session['primary_identity'])
    jobtemplate['archivePath'] = archival_path
    jobtemplate['parameters']['model_type'] = model_type
    jobtemplate['parameters']['model_indexes'] = model_index
    jobtemplate['notifications'][1]['url'] = session['email']
    jobtemplate['notifications'][2]['url'] = session['email']

    print ""
    print "GET_JOB:"
    print pprint(jobtemplate)
    resp = post_result(app.config['JOB_URL_BASE'], None, j_tokens['access_token'], 'json', jobtemplate)

    return resp

def job_permission(job_id):
    '''Update user permissions for a particular job'''
    j_tokens = json.loads(session['tokens'])
    path = '{}/{}/{}'.format(job_id, 'pems', app.config['ADMIN_USER'])
    perm = 'permission=ALL'
    resp = post_result(app.config['JOB_URL_BASE'], path, j_tokens['access_token'], 'data', perm)
    print 'Result: ', resp[1]
    return resp

def is_safe_redirect_url(target):
    # print 'yoooooooooooooooooo', urlparse, urljoin
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in ('http', 'https') and host_url.netloc == redirect_url.netloc

def get_safe_redirect():
    """see https://security.openstack.org/guidelines/dg_avoid-unvalidated-redirects.html"""
    url = request.args.get('next')
    if url and is_safe_redirect_url(url):
        return url
    url = request.referrer
    if url and is_safe_redirect_url(url):
        return url
    return '/'

def get_revoke():
    j_tokens = json.loads(session['tokens'])
    a_token = dict(token='{}'.format(j_tokens['access_token']))
    resp = requests.post(j_tokens['revoke_uri'],
                         auth=(j_tokens['client_id'], j_tokens['client_secret']),
                         data=a_token,
                         verify=False)
    resp.raise_for_status()
    print 'status code for the revoke: ', resp.status_code

##########
# ROUTES #
##########

# @app.route('/')
# def nsides_main():
#     return render_template('nsides_main.html')

# @app.route('/r/<drugs>')
# @app.route('/r/<drugs>/<outcomes>')
# @app.route('/r/<drugs>/<outcomes>/<models>')
# def nsides_main_purl(drugs=None, outcomes=None, models=None):
#     return render_template('nsides_main.html')



@app.route('/jobsubmission/submit-job', methods=['GET', 'POST'])
@authenticated
def submit_job():
    print request.method

    # if request.method == 'GET':
    #     return render_template('jobsubmission.html')

    if request.method == 'POST':
        print "REQUEST: ", json.dumps(request.form, indent=2)
        if not request.form.get('mtype'):
            flash('Please select a model type.')
            return redirect(url_for('submit_job'))
        if not request.form.get('model_index'):
            flash('Please enter a drug index.')
            return redirect(url_for('submit_job'))

        job = get_job(request.form.get('mtype'), request.form.get('model_index'))
        if job[0]:
            result = job_permission(job[1]['id'])
            if not result[0]:
                flash('Job permission error: '+result[1])
            flash('Job request submitted successfully. Job ID: ' + job[1]['id'])
        else:
            flash('Job request was not submitted. Error: ' + job[1])

        return redirect(url_for('job_list'))

@app.route('/profile/data', methods=['GET', 'POST'])
@authenticated
def profile():
    """Show user profile information"""
    if request.method == 'GET':
        identity_id = session.get('primary_identity')
        profile = udb.load_profile(identity_id)

        if profile:
            name, email, institution = profile

            session['name'] = name
            session['email'] = email
            session['institution'] = institution
        
        else:
            flash('Please complete any missing profile fields and press "save".')

        if request.args.get('next'):
            session['next'] = get_safe_redirect()

        if profile:
            return jsonify({'name':name, 'email':email, 'institution':institution})
        else:
            return jsonify({'name':'None', 'email':'None', 'institution':'None'})
        # return render_template('profile.html')

    elif request.method == 'POST':
        name = session['name'] = request.form['name']
        email = session['email'] = request.form['email']
        institution = session['institution'] = request.form['institution']

        udb.save_profile(identity_id=session['primary_identity'],
                         name=name,
                         email=email,
                         institution=institution)
        
        flash('Thank you! Your profile has been successfully updated.')

        if 'next' in session:
            redirect_to = session['next']
            session.pop('next')
        else:
            redirect_to = '/profile'

        return redirect(redirect_to)

@app.route('/signup', methods=['GET'])
def signup():
    """Send the user to Agave Auth"""
    return redirect(app.config['SIGNUP'])

@app.route('/api')
def api():
    return render_template('nsides_api.html')

@app.route('/joblist/data', methods=['GET'])
@authenticated
def job_list():
    j_tokens = json.loads(session['tokens'])
    job_list = get_result(app.config['JOB_URL_BASE'], '', j_tokens['access_token'])
    return jsonify(job_list)
    # return render_template('job_list.html', joblist=job_list)


# API STUFF

@app.route('/api/v1/nsides/estimateForDrug_Outcome')
def api_nsides_estimateForDrug_Outcome():
    return api_call('nsides', 'estimateForDrug_Outcome')

@app.route('/api/v1/nsides/topOutcomesForDrug')
def api_nsides_topOutcomesForDrug():
    return api_call('nsides', 'topOutcomesForDrug')

@app.route('/api/v1/druginfo/jobIndexes')
def api_druginfo_jobIndexes():
    return api_call('druginfo', 'jobIndexes')

@app.route('/api/v1/gote/gpcrFromUniprot')
def api_gote_gpcrFromUniprot():
    return api_call('gpcr', 'gpcrFromUniprot')

@app.route('/api/v1/lab/ae_to_lab')
def api_lab_ae_to_lab():
    return api_call('lab', 'ae_to_lab')

@app.route('/api/v1/omop/reference')
def api_omop_reference():
    return api_call('omop', 'reference')

@app.route('/api/v1/omop/conceptsToName')
def api_omop_conceptsToName():
    return api_call('omop', 'conceptsToName')

@app.route('/api/v1/sider/drugForEffect')
def api_sider_drugForEffect():
    return api_call('sider', 'drugForEffect')

@app.route('/api/v1/sider/drugForEffectFreq')
def api_sider_drugForEffectFreq():
    return api_call('sider', 'drugForEffectFreq')

@app.route('/api/v1/sider/search_term')
def api_sider_search_term():
    return api_call('sider', 'search_term')

@app.route('/api/v1/va/get_ddi_alerts')
def api_va_get_ddi_alerts():
    return api_call('va', 'get_ddi_alerts')

@app.route('/api/v1/snomed/getOutcomeFromSnomedId')
def api_snomed_getOutcomeFromSnomedId():
    return api_call('snomed', 'getOutcomeFromSnomedId')

@app.route('/api/v1/aeolus/ingredientList')
def api_aeolus_ingredientList():
    return api_call('aeolus', 'ingredientList')

@app.route('/api/v1/aeolus/drugReactionCounts')
def api_aeolus_drugReactionCounts():
    return api_call('aeolus', 'drugReactionCounts')

@app.route('/api/v1/aeolus/drugpairReactionCounts')
def api_aeolus_drugpairReactionCounts():
    return api_call('aeolus', 'drugpairReactionCounts')

@app.route('/api/v1/aeolus/reactionListSNOMED')
def api_aeolus_reactionListSNOMED():
    return api_call('aeolus', 'reactionListSNOMED')

@app.route('/api/v1/aeolus/reactionListMedDRA')
def api_aeolus_reactionListMedDRA():
    return api_call('aeolus', 'reactionListMedDRA')

@app.route('/api/v1/aeolus/drugpairList')
def api_aeolus_drugpairList():
    return api_call('aeolus', 'drugpairList')

@app.route('/api/v1/aeolus/drugpairReactionListMedDRA')
def api_aeolus_drugpairReactionListMedDRA():
    return api_call('aeolus', 'drugpairReactionListMedDRA')

@app.route('/api/v1/query')
def api_call(service = None, meta = None, query = None):
    #ipdb.set_trace()
    if service is None:
        service = request.args.get('service')
    if meta is None:
        meta = request.args.get('meta')
    if query is None:
        query = request.args.get('q')

    print "Service: ",service
    print "Meta/Method: ",meta
    print "Query: ",query

    if service == [''] or service is None:
        response.status = 400
        return 'No service selected'
    elif len(service) == 1:
        json = '''{"results": "result"}'''

    # MongoDB (nSides)
    elif service == 'nsides':
        # e.g. /api/v1/query?service=nsides&meta=estimateForDrug_Outcome&drugs=19097016&outcome=4294679&model=nopsm
        if meta == 'estimateForDrug_Outcome':
            #drugs = [drug.replace('|',',') for drug in request.params.get('drugs').split(',')]
            # ^ Separate individual drugs using comma. Drug class represented as `DrugA|DrugB|etc`
            drugs = request.args.get('drugs')
            all_drugs_ingredients = convertDrugsToIngredients(drugs)
            if drugs == [''] or drugs is None:
                response.status = 400
                return 'No drug(s) selected'

            outcome = request.args.get('outcome')
            if outcome == [''] or outcome is None:
                response.status = 400
                return 'No outcome selected'

            model_type = request.args.get('model')
            if model_type == [''] or model_type is None:
                model_type = 'all'

            query = {'drugs': all_drugs_ingredients, 'outcome': outcome, 'model': model_type}
            # print "Parsed query:", query

            service_result = query_nsides_mongo.query_db(service, meta, query)
            json = '''{"results": %s}''' %(str(service_result))

        # e.g. /api/v1/query?service=nsides&meta=topOutcomesForDrug&numResults=10&drugs=19097016
        elif meta == 'topOutcomesForDrug': #'get_top_10_effects':
            drugs = request.args.get('drugs')
            # print type(drugs), drugs
            all_drugs_ingredients = convertDrugsToIngredients(drugs)

            print('DRUGS:'), 'ingredients', all_drugs_ingredients
            # print(drugs)
            if drugs == [''] or drugs is None:
                response.status = 400
                return 'No drug(s) selected'

            num_results = request.args.get('numResults')
            if num_results == [''] or num_results is None:
                num_results = 10

            model_type = request.args.get('model')
            if model_type == [''] or model_type is None:
                model_type = 'all'

            query = {'drugs': all_drugs_ingredients, 'numResults': num_results, 'model': model_type}
            # print "Parsed query:", query

            service_result = query_nsides_mongo.query_db(service, meta, query)
            json = '''{"results": %s}''' %(str(service_result))

    elif service == 'druginfo':
        # e.g. /api/v1/query?service=druginfo&meta=jobIndexes&drugs=19097016
        if meta == 'jobIndexes':
            drugs = request.args.get('drugs')
            if drugs == [''] or drugs is None:
                response.status = 400
                return 'No drug(s) selected'
            query = {'drugs': drugs}
            service_result = query_nsides_mongo.query_db(service, meta, query)
            json = '''{"results": %s}''' %(str(service_result))
        
    elif service == 'gpcr':
        if meta == 'gpcrFromUniprot':
            uniprot_id = request.args.get('uniprot')
            if uniprot_id == [''] or uniprot_id is None:
                response.status = 400
                return 'No Uniprot ID provided'
            query = {'uniprot': uniprot_id}
            service_result = query_nsides_mongo.query_db(service, meta, query)
            #json = service_result
            json = '''{"results": %s}''' %(str(service_result))

    # MySQL
    elif service == 'lab':
        if meta == 'ae_to_lab':
            service_result = query_nsides_mysql.query_db(service, meta, query)
            json = '''{"results": %s}''' %(str(service_result))
    elif service == 'omop':
        if meta == 'reference':
            service_result = query_nsides_mysql.query_db(service, meta, query)
            json = '''{"results": %s}''' %(str(service_result))
        elif meta == 'conceptsToName':
            service_result = query_nsides_mysql.query_db(service, meta, query)
            json = '''{"results": %s}''' %(str(service_result))
    elif service == 'sider':
        if meta == 'drugForEffect':
            service_result = query_nsides_mysql.query_db(service, meta, query)
            json = '''{"results": %s}''' %(str(service_result))
        elif meta == 'drugForEffectFreq':
            service_result = query_nsides_mysql.query_db(service, meta, query)
            json = '''{"results": %s}''' %(str(service_result))
        elif meta == 'search_term':
            json = '''{"results": [c1, c2, c3 ... cn]} CONCEPT_ID'''
    elif service == 'va':
        if meta == 'get_ddi_alerts':
            service_result = query_nsides_mysql.query_db(service, meta, query)
            json = '''{"results": %s}''' %(str(service_result))
    elif service == 'snomed':
        if meta == 'getOutcomeFromSnomedId':
            service_result = query_nsides_mysql.query_db(service, meta, query)
            json = '''{"results": %s}''' %(str(service_result))
    elif service == 'aeolus':
        if meta == 'ingredientList':
            service_result = query_nsides_mysql.query_db(service, meta)
            json = '''{"results": %s}''' %(str(service_result))
        elif meta == 'drugReactionCounts':
            service_result_1 = query_nsides_mysql.query_db(service, meta, query)
            #service_result_2 = query_nsides_mysql.query_db(service, meta)
            #json = '''{"results": %s, "nrows": %s}, ''' %(str(service_result_1), str(service_result_2))
            json = '''%s''' %(str(service_result_1))
        elif meta == 'drugpairReactionCounts':
            #service_result = query_nsides_mysql.query_db(service, meta, query)
            #json = '''{"results": %s}''' %(str(service_result))
            service_result_1 = query_nsides_mysql.query_db(service, meta, query)
            json = '''%s''' %(str(service_result_1))
        elif meta == 'reactionListSNOMED':
            service_result = query_nsides_mysql.query_db(service, meta)
            json = '''{"results": %s}''' %(str(service_result))
        elif meta == 'reactionListMedDRA':
            service_result = query_nsides_mysql.query_db(service, meta)
            json = '''{"results": %s}''' %(str(service_result))
        elif meta == 'drugpairList':
            service_result = query_nsides_mysql.query_db(service, meta)
            json = '''{"results": %s}''' %(str(service_result))
        elif meta == 'drugpairReactionListMedDRA':
            service_result  = query_nsides_mysql.query_db(service, meta)
            json = '''{"results": %s}''' %(str(service_result))
    else:
        json = '''{"": ""}'''

    json = json.replace("'", '"')
    print 'Completing requests with ', json[0:14]
    return json

###################
#     ROUTES      #
#################
@app.route('/login', methods=['GET'])
def login():
    """Send the user to Agave Auth."""
    print 'sending user to agave auth'
    return redirect(url_for('authcallback'))

@app.route('/logout', methods=['GET'])
@authenticated
def logout():
    """
    - Revoke tokens with Agave Auth
    - Destroy session state
    - Redirect user to the Agave Auth logout page
    """
    get_revoke()
    session.clear()
    # redirect_uri = url_for('nsides_main', _external=True)
    return redirect('/')

@app.route('/authcallback', methods=['GET'])
def authcallback():
    """Handles interaction with Agave Auth service."""
    if 'error' in request.args:
        flash("We couldn't log you into the portal: " + request.args.get('error_description', request.args['error']))
        return redirect(url_for('nsides_main'))
    print 'url was ', url_for('authcallback')
    redirect_uri = url_for('authcallback', _external=True)
    print 'redirect uri\n ', redirect_uri
    client = load_portal_client(redirect_uri)
    print 'client\n ', client
    auth_uri = client.step1_get_authorize_url()
    print 'auth uri\n ', auth_uri
    
    if 'code' not in request.args:
        # if no 'code' query string parameter, start Agave Auth login flow
        auth_uri = client.step1_get_authorize_url()
        print 'starting agave auth login with\n', auth_uri
        return redirect(auth_uri)
    else:
        # otherwise, we're coming back from Agave Auth; start to exchange auth code for token
        code = request.args.get('code')
        print 'code', code
        tokens = client.step2_exchange(code)
        tokens.revoke_uri = app.config['REVOKE_URL']
        token_json = tokens.to_json()
        print 'token json',token_json
        
        user_profile = get_result(app.config['PROFILE_URL_BASE'],
                                    'me',
                                    tokens.access_token)
        if user_profile[0]:
            print 'username',user_profile[1]['username']
        else:
            flash("User profile was not retrieved. Error:" + user_profile[1])

        session.update(
            tokens=tokens.to_json(),
            is_authenticated=True,
            name=user_profile[1]['full_name'],
            email=user_profile[1]['email'],
            institution='',
            primary_identity=user_profile[1]['username']
        )

        profile = udb.load_profile(session['primary_identity'])
        if profile:
            name, email, institution = profile
            session['name'] = name
            session['email'] = email
            session['institution'] = institution
        else:
            udb.save_profile(identity_id=session['primary_identity'],
                                name=session['name'],
                                email=session['email'],
                                institution=session['institution'])
            handle_permission(session['primary_identity'])

            # return redirect(url_for('profile', next=url_for('submit_job')))
            return redirect('/')
        
        # return redirect(url_for('submit_job'))
        return redirect('/jobsubmission')
@app.route('/session')
def get_session():
    if 'primary_identity' in session:
        profile = udb.load_profile(session['primary_identity'])
        name, email, institution = profile
        obj = {
            'name': name,
            'email': email,
            'institution': institution
        }
        return jsonify(obj)
    return jsonify({})

@app.route('/serve_bundle')#production
def serve_bundle():
    resp = make_response(send_from_directory('../Frontend/dist/', 'bundle.a3bd4f51c9b453455638.js.gz'))
    resp.headers['Content-Encoding'] = 'gzip'
    return resp

# @app.route('/serve_bundle')#development
# def serve_bundle():
#     resp = make_response(send_from_directory('../Frontend/dist/', 'bundle.js'))
#     return resp

@app.route('/')
def home():
    return render_template("nsides.html")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
@authenticated
def catch_all(path):
    print 'fell in catchall'
    return render_template("nsides.html")

if __name__ == "__main__":
    app.run(host='localhost',
    ssl_context=('static/nsides.crt', 'static/nsides.key'))
