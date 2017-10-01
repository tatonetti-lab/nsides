"""
NSIDES

The nSides web front-end, implemented in Flask

@author: Joseph D. Romano
@author: Rami Vanguri

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

from flask_wtf import FlaskForm
from wtforms import Form, StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired


class LoginForm(Form):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    rememberme = BooleanField('remember')


#########
# INITS #
#########

app = Flask(__name__)
app.secret_key = 'changeme'
app.config.from_envvar('NSIDES_FRONTEND_SETTINGS', silent=True)

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

udb = UserDb()
        

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

@app.route('/login', methods=['GET', 'POST'])
def login():
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

@app.route('/api')
def api():
    return render_template('nsides_api.html')


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
