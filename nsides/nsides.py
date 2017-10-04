"""
NSIDES

The nSides web front-end, (re)implemented in Flask

@author: Joseph D. Romano
@author: Rami Vanguri
@author: Choonhan Youn

(c) 2017 Tatonetti Lab

"""

import os
import ipdb
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, make_response
import query_nsides_mongo
import query_nsides_mysql
from werkzeug.security import check_password_hash, generate_password_hash
import flask_login
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from functools import wraps
import requests
import click
import json
from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import Form, StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired

from oauth2client.client import flow_from_clientsecrets


class LoginForm(Form):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    rememberme = BooleanField('remember')

def authenticated(fn):
    """Decorator for requiring authentication on a route."""
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        if not session.get('is_authenticated'):
            return redirect(url_for('login', next=request.url))
        if request.path == '/logout':
            return fn(*args, **kwargs)
        return fn(*args, **kwargs)
    return decorated_function

#########
# INITS #
#########

app = Flask(__name__)
app.secret_key = 'changeme'
#app.config.from_envvar('NSIDES_FRONTEND_SETTINGS', silent=True)
app.config.from_pyfile('nsides_flask.conf')

with open(app.config['JOB_TEMPLATE']) as f:
    jobtemplate = json.load(f)

login_manager = flask_login.LoginManager()
login_manager.session_protection = "strong"
login_manager.init_app(app)

MONGODB_HOST, MONGODB_UN, MONGODB_PW = open('./nsides-mongo.cnf').read().strip().split('\n')
MONGODB_PORT = 27017

class UserDb(object):
    def __init__(self):
        self.client = MongoClient('mongodb://%s:%s@%s:%s/nsides_dev' % (MONGODB_UN, MONGODB_PW, MONGODB_HOST, MONGODB_PORT))
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
    return flow

def get_result(base_url, path, access_token):
    req_url = '{}/{}{}'.format(base_url, path, '?pretty=true')
    print 'GET request url:',req_url
    req_headers = dict(Authorization='Bearer {}'.format(access_token))
    resp = requests.get(req_url,
                        headers=req_headers,
                        verify=False)
    # resp.raise_for_status()
    print 'Status code:', resp.status_code
    resp_result = resp.json()
    print 'Response:', resp_result

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
    print 'POST request url:', req_url
    req_headers = dict(Authorization='Bearer {}'.format(access_token))
    if data_type == 'json':
        resp = requests.post(req_url, headers=req_headers, json=post_data, verify=False)
    elif data_type == 'data':
        resp = requests.post(req_url, headers=req_headers, data=post_data, verify=False)
    else:
        resp = 'Please choose the data type: "json" or "data"'
        print resp
        return False, resp

    print 'Status code:', resp.status_code
    resp_result = resp.json()
    print 'Response:', resp_result
    
    if 'status' in resp_result:
        if resp_result['status'] == 'error':
            print 'error message:', resp_result['message']
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

    print jobtemplate
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

##############
# USER CLASS #
##############

class User(flask_login.UserMixin):
    def __init__(self, email):
        self.email = email

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def get_id(self):
        return self.email

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)

# Some testing data
users = {'foo@bar.tld': {'pw': 'secret'}}

@login_manager.user_loader
def user_loader(email):
    u = udb.users.find_one({"_id": email})
    if not u:
        return None
    return User(u['_id'])


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    # CHANGE THIS!
    user.is_authenticated = request.form['pw'] == users[email]['pw']

    return user

@login_manager.unauthorized_handler
def unauthorized_handler():
    flash("Error: You have to log in to access this page")
    return redirect(url_for('nsides_main'))

##########
# ROUTES #
##########

@app.route('/')
def nsides_main():
    return render_template('nsides_main.html')

@app.route('/loginold', methods=['GET', 'POST'])
def login_old():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        print "got here"
        user = udb.users.find_one({"_id": form.email.data})
        print(user)
        if user and User.validate_login(user['pw_hash'], form.password.data):
            user_obj = User(user['_id'])
            flask_login.login_user(user_obj)
            flash("Logged in successfully", category="success")
            return redirect(url_for('nsides_main'))
        flash("Wrong email or password", category='error')
    return render_template('nsides_login.html', form=form)

@app.route('/login', methods=['GET'])
def login():
    """Send the user to Agave Auth."""
    return redirect(url_for('authcallback'))

@app.route('/authcallback', methods=['GET'])
def authcallback():
    """Handles interaction with Agave Auth service."""
    if 'error' in request.args:
        flash("We couldn't log you into the portal: " + request.args.get('error_description', request.args['error']))
        return redirect(url_for('nsides_main'))

    redirect_uri = url_for('authcallback', _external=True)
    client = load_portal_client(redirect_uri)
    auth_uri = client.step1_get_authorize_url()
    print 'auth uri', auth_uri
    
    if 'code' not in request.args:
        # if no 'code' query string parameter, start Agave Auth login flow
        auth_uri = client.step1_get_authorize_url()
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

            return redirect(url_for('profile', next=url_for('submit_job')))
        
        return redirect(url_for('submit_job'))

@app.route('/jobsubmission', methods=['GET', 'POST'])
@authenticated
def submit_job():
    if request.method == 'GET':
        return render_template('jobsubmission.html')

    if request.method == 'POST':
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

@app.route('/protected')
@flask_login.login_required
def protected():
    flash('This is a secret message', category="success")
    flash('Logged in as: ' + flask_login.current_user.email, category="succes")

@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    flash("Logged out successfully", category="success")
    return redirect(url_for('nsides_main'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # TODO: Validate user agrees
        print request.form
        name = request.form['name']
        institution = request.form['institution']
        email = request.form['email']
        pw1 = request.form['password1']
        pw2 = request.form['password2']
        if pw1 != pw2:
            flash('Passwords don\'t match')
            return redirect(url_for('signup'))
        if udb.submit_new_user(name, institution, email, pw1):
            flash('Signup success! Please log in.')
            return redirect(url_for('login'))
        return redirect(url_for('signup'))
    return render_template('nsides_signup.html')

@app.route('/signupagave', methods=['GET'])
def signupagave():
    """Send the user to Agave Auth"""
    return redirect(app.config['SIGNUP'])

@app.route('/api')
def api():
    return render_template('nsides_api.html')

@app.route('/joblist', methods=['GET'])
@authenticated
def job_list():
    j_tokens = json.loads(session['tokens'])
    job_list = get_result(app.config['JOB_URL_BASE'], '', j_tokens['access_token'])
    return render_template('job_list.html', joblist=job_list)


# BEACON STUFF
# are these still necessary?

@app.route('/beacon/<service>/concepts')
def getConcepts(service):
    keywords = request.params.get('keywords')
    semgroup = request.params.get('semgroup')
    pageNumber = request.params.get('pageNumber')
    pageSize = request.params.get('pageSize')
    meta = 'getConcepts'
    beacon_result = query_nsides_mysql.query_db(service, str(meta), 'cancer')
    json = '''%s''' %(str(beacon_result))
    json = json.replace("'", '"')
    response.content_type = 'application/json'
    return json

@app.route('/beacon/<service>/concepts/<conceptId>')
def getConceptDetails(service, conceptId):
    keywords = request.params.get('keywords')
    semgroup = request.params.get('semgroup')
    pageNumber = request.params.get('pageNumber')
    pageSize = request.params.get('pageSize')
    meta = 'getConceptDetails'
    beacon_result = query_nsides_mysql.query_db(service, str(meta), conceptId)
    json = '''%s''' %(str(beacon_result))
    json = json.replace("'", '"')
    response.content_type = 'application/json'
    return json

@app.route('/beacon/<service>/evidence/<statementId>')
def getEvidence(service, statementId):
    json = []
    response.content_type = 'application/json'
    return '[]'

@app.route('/beacon/<service>/exactmatches')
def getExactMatchesToConceptList(service):
    json = []
    response.content_type = 'application/json'
    return '[]'

@app.route('/beacon/<service>/exactmatches/<conceptId>')
def getExactMatchesToConcept(service, conceptId):
    json = []
    response.content_type = 'application/json'
    return '[]'

@app.route('/beacon/<service>/statements')
def getStatemetns(service):
    json = []
    response.content_type = 'application/json'
    return '[]'



# API STUFF

@app.route('/api/v1/query')
def api_call():
    #ipdb.set_trace()
    service = request.args.get('service')
    meta = request.args.get('meta')
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
            if drugs == [''] or drugs is None:
                response.status = 400
                return 'No drug(s) selected'

            outcome = request.args.get('outcome')
            if outcome == [''] or outcome is None:
                response.status = 400
                return 'No outcome selected'

            model_type = request.args.get('model')
            if model_type == [''] or model_type is None:
                model_type = 'dnn'

            query = {'drugs': drugs, 'outcome': outcome, 'model': model_type}
            print "Parsed query:", query

            service_result = query_nsides_mongo.query_db(service, meta, query)
            json = '''{"results": %s}''' %(str(service_result))

        # e.g. /api/v1/query?service=nsides&meta=topOutcomesForDrug&numResults=10&drugs=19097016
        elif meta == 'topOutcomesForDrug': #'get_top_10_effects':
            drugs = request.args.get('drugs')
            print('DRUGS:')
            print(drugs)
            if drugs == [''] or drugs is None:
                response.status = 400
                return 'No drug(s) selected'

            num_results = request.args.get('numResults')
            if num_results == [''] or num_results is None:
                num_results = 10

            model_type = request.args.get('model')
            if model_type == [''] or model_type is None:
                model_type = 'dnn'

            query = {'drugs': drugs, 'numResults': num_results, 'model': model_type}
            print "Parsed query:", query

            service_result = query_nsides_mongo.query_db(service, meta, query)
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
    elif service == 'omop':
        if meta == 'reference':
            service_result = query_nsides_mysql.query_db(service, meta, query)
            json = '''{"results": %s}''' %(str(service_result))

    else:
        json = '''{"": ""}'''

    json = json.replace("'", '"')

    #ipdb.set_trace()
    #response.content_type = 'application/json'

    return json

if __name__ == "__main__":
    app.run(host='localhost',
    ssl_context=('static/nsides.crt', 'static/nsides.key'))