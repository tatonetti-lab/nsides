# from bottle import route, run, template
from bottle import default_app, route, static_file, request, response, template
import pymysql
import query_nsides_mysql
import query_nsides_mongo

@route('/')
def index():
    return static_file("nsides_splash.html", root='')

@route('/api')
def api():
    return static_file("nsides_api.html", root='')

@route('/dev')
def dev():
    return static_file("nsides_dev.html", root='')

@route('/dev2')
def dev2():
    return static_file("nsides_dev-ci.html", root='')

@route('/index/css/<cssfile>')
def static_css(cssfile):
    return static_file(cssfile, root='index/css/')

@route('/index/data/<datafile>')
def static_css(datafile):
    return static_file(datafile, root='index/data/')

@route('/index/fonts/<fontfile>')
def static_font(fontfile):
    return static_file(fontfile, root='index/fonts/')

@route('/index/img/<imgfile>')
def static_img(imgfile):
    return static_file(imgfile, root='index/img/')

@route('/index/js/<jsfile>')
def static_css(jsfile):
    return static_file(jsfile, root='index/js/')

@route('/index/misc/<miscfile>')
def static_font(miscfile):
    return static_file(miscfile, root='index/misc/')


# Beacon
@route('/beacon/<service>/concepts')
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

@route('/beacon/<service>/concepts/<conceptId>')
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

@route('/beacon/<service>/evidence/<statementId>')
def getEvidence(service, statementId):
    json = []
    response.content_type = 'application/json'
    return '[]'

@route('/beacon/<service>/exactmatches')
def getExactMatchesToConceptList(service):
    json = []
    response.content_type = 'application/json'
    return '[]'

@route('/beacon/<service>/exactmatches/<conceptId>')
def getExactMatchesToConcept(service, conceptId):
    json = []
    response.content_type = 'application/json'
    return '[]'

@route('/beacon/<service>/statements')
def getStatemetns(service):
    json = []
    response.content_type = 'application/json'
    return '[]'


# API
@route('/api/v1/query')
def api_call():
    service = request.params.get('service')
    meta = request.params.get('meta')
    query = request.params.get('q')

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
            drugs = request.params.get('drugs')
            if drugs == [''] or drugs is None:
                response.status = 400
                return 'No drug(s) selected'

            outcome = request.params.get('outcome')
            if outcome == [''] or outcome is None:
                response.status = 400
                return 'No outcome selected'

            model_type = request.params.get('model')
            if model_type == [''] or model_type is None:
                model_type = 'dnn'

            query = {'drugs': drugs, 'outcome': outcome, 'model': model_type}
            print "Parsed query:", query

            service_result = query_nsides_mongo.query_db(service, meta, query)
            json = '''{"results": %s}''' %(str(service_result))

        # e.g. /api/v1/query?service=nsides&meta=topOutcomesForDrug&numResults=10&drugs=19097016
        elif meta == 'topOutcomesForDrug': #'get_top_10_effects':
            drugs = request.params.get('drugs')
            if drugs == [''] or drugs is None:
                response.status = 400
                return 'No drug(s) selected'

            num_results = request.params.get('numResults')
            if num_results == [''] or num_results is None:
                num_results = 10

            model_type = request.params.get('model')
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

    response.content_type = 'application/json'

    return json

# run(host='localhost', port=8080)
application = default_app()

if __name__ == '__main__':
    application.run(host='0.0.0.0') #, debug=True)
