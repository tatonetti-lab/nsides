# from bottle import route, run, template
from bottle import default_app, route, static_file, request, response, template
import pymysql
import query_nsides_aws

@route('/')
def index():
    return static_file("nsides.html", root='')

@route('/api')
def faq():
    return static_file("api.html", root='')

@route('/index/css/<cssfile>')
def static_css(cssfile):
    return static_file(cssfile, root='index/css/')

@route('/index/img/<imgfile>')
def static_img(imgfile):
    return static_file(imgfile, root='index/img/')

@route('/index/fonts/<fontfile>')
def static_font(fontfile):
    return static_file(fontfile, root='index/fonts/')

@route('/index/misc/<miscfile>')
def static_font(miscfile):
    return static_file(miscfile, root='index/misc/')

@route('/beacon/<service>/concepts')
def getConcepts(service):
    keywords = request.params.get('keywords')
    semgroup = request.params.get('semgroup')
    pageNumber = request.params.get('pageNumber')
    pageSize = request.params.get('pageSize')
    meta = 'getConcepts'
    beacon_result = query_nsides_aws.query_db(service, str(meta), 'cancer')
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
    beacon_result = query_nsides_aws.query_db(service, str(meta), conceptId)
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


@route('/api/v1/query')
def api_call():
    service = request.params.get('service')
    meta = request.params.get('meta')
    query = request.params.get('q')

    print "Service: ",service
    print "Meta/Method: ",meta
    print "Query: ",query

    if service == ['']:
        response.status = 400
        return 'No service selected'
    elif len(service) == 1:
        json = '''{"results": "result"}'''
    elif service == 'sider':
        if meta == 'drugForEffect':
            service_result = query_nsides_aws.query_db(service, meta, query)
            json = '''{"results": %s}''' %(str(service_result))
        elif meta == 'search_term':
            json = '''{"results": [c1, c2, c3 ... cn]} CONCEPT_ID'''
    elif service == 'aeolus':
        if meta == 'ingredientList':
            service_result = query_nsides_aws.query_db(service, meta)
            json = '''{"results": %s}''' %(str(service_result))
        elif meta == 'drugReactionCounts':
            service_result_1 = query_nsides_aws.query_db(service, meta, query)
            #service_result_2 = query_nsides_aws.query_db(service, meta)
            #json = '''{"results": %s, "nrows": %s}, ''' %(str(service_result_1), str(service_result_2))
            json = '''%s''' %(str(service_result_1))
        elif meta == 'drugpairReactionCounts':
            #service_result = query_nsides_aws.query_db(service, meta, query)
            #json = '''{"results": %s}''' %(str(service_result))
            service_result_1 = query_nsides_aws.query_db(service, meta, query)
            json = '''%s''' %(str(service_result_1))
        elif meta == 'reactionListSNOMED':
            service_result = query_nsides_aws.query_db(service, meta)
            json = '''{"results": %s}''' %(str(service_result))
        elif meta == 'reactionListMedDRA':
            service_result = query_nsides_aws.query_db(service, meta)
            json = '''{"results": %s}''' %(str(service_result))
        elif meta == 'drugpairList':
            service_result = query_nsides_aws.query_db(service, meta)
            json = '''{"results": %s}''' %(str(service_result))
        elif meta == 'drugpairReactionListMedDRA':
            service_result  = query_nsides_aws.query_db(service, meta)
            json = '''{"results": %s}''' %(str(service_result))
    elif service == 'omop':
        if meta == 'reference':
            service_result = query_nsides_aws.query_db(service, meta, query)
            json = '''{"results": %s}''' %(str(service_result))
    else:
        json = '''{"": ""}'''

    json = json.replace("'", '"')

    response.content_type = 'application/json'

    return json

# run(host='localhost', port=8080)
application = default_app()

if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True)