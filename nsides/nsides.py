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

app = Flask(__name__)
app.config.from_envvar('NSIDES_FRONTEND_SETTINGS', silent=True)

@app.route('/')
def nsides_main():
    return render_template('nsides_main.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('nsides_login.html')

@app.route('/logout')
def logout():
    return render_template('nsides_logout.html')

@app.route('/signup')
def signup():
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
