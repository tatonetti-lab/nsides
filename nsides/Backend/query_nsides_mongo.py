"""
query_nsides_mongo.py

Connects to MongoDB and extracts records for API's usage

@author Victor Nwankwo, 2017
@author Tal Lorberbaum, 2017
@author Joe Romano, 2017
@author: Kai Xiang Chen, 2018

USAGE:

Ensure that nsides-mongo.cnf file exists


"""

import sys
import pymongo
from pymongo import UpdateOne
from operator import itemgetter
import json
import query_nsides_mysql
from nsides_helpers import allIngredientRxnormToName, mongodbRxnormToName, effectsSnomedToName
import urllib

import ipdb

urlopen = urllib.urlopen

EXTRACTED_DIR = './results/extracted'
REFERNCE_DIR = './reference'
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

# Document Structure
# {
#     'rxnorm': 0,
#     'snomed': 0,
#     'model': 'none',
#     'estimates': [
#         {'year': 1990,
#         'prr': 1.5,
#         'ci': 0.1},
#         {'year': 1991,
#         'prr': 1.6,
#         'ci': 0.2}
#     ],
#     'nreports': 0
# }

def main():
    
    print >> sys.stderr, "Loading password from ./nsides-mongo.cnf..."
    MONGODB_HOST, MONGODB_UN, MONGODB_PW = open('./nsides-mongo.cnf').read().strip().split('\n')
    
    client = pymongo.MongoClient('mongodb://%s:%s@%s:%s/nsides_in?authSource=admin' % (MONGODB_UN, MONGODB_PW, MONGODB_HOST, MONGODB_PORT))
    db = client.nsides_in
    estimates = db.estimates

    print >> sys.stderr, "%s" % db.collection_names()
    print >> sys.stderr, "%s" % str(estimates.count())

    query_db('nsides', 'estimateForDrug_Outcome', {'drugs': '19097016', 'model': 'dnn', 'outcome': '4294679'})

    return True

def connect():
    print "Connecting to the API..."

    # Connect to MongoDB database
    print "Connecting to database"

    print >> sys.stderr, "Loading password from ./nsides-mongo.cnf..."
    MONGODB_HOST, MONGODB_UN, MONGODB_PW = open('./nsides-mongo.cnf').read().strip().split('\n')

    # print 'MongoDB host: ', MONGODB_HOST
    # print 'MongoDB username: ', MONGODB_UN
    # print 'MongoDB password: ', MONGODB_PW
    
    client = pymongo.MongoClient('mongodb://%s:%s@%s:%s/nsides_in?authSource=admin' % (MONGODB_UN, MONGODB_PW, MONGODB_HOST, MONGODB_PORT))
    return client


def query_db(service, method, query=False, cache=False):

    print "Connecting to the API..."

    # Connect to MongoDB database
    print "Connecting to database"

    print >> sys.stderr, "Loading password from ./nsides-mongo.cnf..."
    MONGODB_HOST, MONGODB_UN, MONGODB_PW = open('./nsides-mongo.cnf').read().strip().split('\n')

    # print 'MongoDB host: ', MONGODB_HOST
    # print 'MongoDB username: ', MONGODB_UN
    # print 'MongoDB password: ', MONGODB_PW
    
    client = pymongo.MongoClient('mongodb://%s:%s@%s:%s/nsides_in?authSource=admin' % (MONGODB_UN, MONGODB_PW, MONGODB_HOST, MONGODB_PORT))
    # db = client.nsides_in
    db = client.nsides_in
    estimates = None
    if len(str(query["drugs"]).split(',')) == 1:
        estimates = db.estimates
    else: 
        estimates = db.estimates_agave
    gpcr = db.gpcr
    
    
    druginfo_db = client.nsides
    druginfo = druginfo_db.druginfo

    json_return = []
    if service == 'nsides':
        print "  Service: ",service
        print "  Method: ", method
        print "  Query : ", query

        if method == 'estimateForDrug_Outcome':
            if query["model"] == 'all':
                estimate_records = estimates.find(
                                    { '$and':
                                        [ { 'rxnorm': query["drugs"] },
                                        { 'snomed': int(query["outcome"]) }
                                        ]
                                    })
                print 'here'
                if estimate_records is None:
                    print "  No record found"

                else:
                    estimate_records = list(estimate_records)
                    for estimate_record in estimate_records:
                        # Sort estimates by year and remove unicode from estimate keys
                        sorted_estimates = sorted(estimate_record[u"estimates"], key=lambda k: k[u'year'])
                        sorted_nreports = sorted(estimate_record[u"nreports"], key=lambda k: k[u'year'])

                        model_type = estimate_record[u"model"]

                        processed_estimates = []
                        for s in sorted_estimates:
                            processed_year_estimate = dict()
                            for k in s.keys():
                                processed_year_estimate[k.encode('ascii','ignore')] = s[k]
                            processed_estimates.append( processed_year_estimate )
                        # print s.keys()
                        # print estimate_record[u"estimates"], '\n'

                        processed_nreports = []
                        for r in sorted_nreports:
                            nreport_for_year = dict()
                            for k in r.keys():
                                nreport_for_year[k.encode('ascii', 'ignore')] = r[k]
                            processed_nreports.append(nreport_for_year)

                        #print "  ", processed_estimates
                        #print "  ", sorted_nreports

                        #processed_nreports = []
                        #for r in sorted_nreports:
                        #    processed_

                        json_return.append({ 
                            # "effect_string" : "estimateForDrug_Outcome",
                            "outcome" : int(estimate_record[u"snomed"]), #query["outcome"],
                            "drug" : estimate_record[u"rxnorm"], #query["drugs"],
                            "estimates": processed_estimates, #estimate_record[u"estimates"]
                            "nreports": processed_nreports,
                            "model": model_type
                        })
            else:
                estimate_record = estimates.find_one(
                                    { '$and':
                                        [ { 'rxnorm': query["drugs"] },
                                        { 'snomed': int(query["outcome"]) },
                                        { 'model': query["model"] }
                                        ]
                                    })
            
                if estimate_record is None:
                    print "  No record found"

                else:
                    # Sort estimates by year and remove unicode from estimate keys
                    sorted_estimates = sorted(estimate_record[u"estimates"], key=lambda k: k[u'year'])
                    sorted_nreports = sorted(estimate_record[u"nreports"], key=lambda k: k[u'year'])

                    processed_estimates = []
                    for s in sorted_estimates:
                        processed_year_estimate = dict()
                        for k in s.keys():
                            processed_year_estimate[k.encode('ascii','ignore')] = s[k]
                        processed_estimates.append( processed_year_estimate )
                    # print s.keys()
                    # print estimate_record[u"estimates"], '\n'

                    processed_nreports = []
                    for r in sorted_nreports:
                        nreport_for_year = dict()
                        for k in r.keys():
                            nreport_for_year[k.encode('ascii', 'ignore')] = r[k]
                        processed_nreports.append(nreport_for_year)

                    #print "  ", processed_estimates
                    #print "  ", sorted_nreports

                    #processed_nreports = []
                    #for r in sorted_nreports:
                    #    processed_

                    json_return.append({ 
                        # "effect_string" : "estimateForDrug_Outcome",
                        "outcome" : int(estimate_record[u"snomed"]), #query["outcome"],
                        "drug" : estimate_record[u"rxnorm"], #query["drugs"],
                        "estimates": processed_estimates, #estimate_record[u"estimates"]
                        "nreports": processed_nreports,
                        "model": query["model"]
                    })

        
        elif method == 'topOutcomesForDrug_old': #'get_top_10_effects':
            # Given drug and model, return top 10 outcomes ordered by 2016 CI
            # For now, fetch all documents and process in Python
            # Also check if we are looking for a subset or ALL results
            if query["numResults"] == 'all':
                num_results = 'all'
            else:
                num_results = int(query["numResults"])
            # print num_results, "number of results"
            
            estimate_record = estimates.find(
                                { '$and':
                                    [ { 'rxnorm': query["drugs"] },
                                      { 'model': query["model"] },
                                      { 'snomed': {'$ne':None} }
                                    ]
                                });
            
            all_outcomes = []
            
            for record in estimate_record:
                #pprint(record)
                for estimate in record[u'estimates']:
                    if estimate[u'year'] == 2016:
                        #all_outcomes.append( (int(record[u'snomed']), estimate[u'ci'], estimate[u'prr']) )
                        all_outcomes.append( (int(record[u'snomed']) ) )
                        # print record[u'snomed'], estimate[u'prr']
                        # all_outcomes.append((record[u'snomed'], estimate[u'prr']))
                        
            print "  ", len(all_outcomes), "total outcomes"

            # sorted(all_outcomes,key=itemgetter(1), reverse=True)[:num_results]
            # Check if we should show all or just a limited number of sorted results
            #ipdb.set_trace()
            if num_results == 'all':
                top_results = sorted(all_outcomes)
            else:
                top_results = sorted(all_outcomes)[:num_results]
            top_outcome_ids = [str(r) for r in top_results]

            if len(top_outcome_ids) == 0:
                return []

            ipdb.set_trace()

            concept_mappings = query_nsides_mysql.query_db(service='omop', method='conceptsToName',
                                                           query= ",".join(top_outcome_ids) )

            concept_id2name = dict()
            for m in concept_mappings:
                concept_id2name[ str(m['concept_id']) ] = m['concept_name']

            outcome_options = []
            for position, concept_id in enumerate(top_outcome_ids): # Added enumeration to list
                if concept_id in concept_id2name:
                    outcome_options.append( { 'value': concept_id, 'label': str(position + 1) + " - " + concept_id2name[concept_id].replace("'", "") } )
            #print("OUTCOME OPTIONS:")
            #print outcome_options

            
            json_return.append({
                    # "effect_string" : "estimateForDrug_Outcome",
                    "topOutcomes" : outcome_options, #top_outcome_ids,
                    "drug" : query["drugs"],
                }) 

            ## Use aggregate to count number of instances of unique drugs
            # estimates_aggregate = estimates.aggregate([
            #     { "$group": {
            #         "_id": "$rxnorm",
            #         "count": { "$sum": 1 }
            #     }}
            # ])
            # 
            # OR 
            #
            # print(record_aggregate)
            # record_aggregate = db.estimates.aggregate([
            #     {"$group":{"_id":"$rxnorm","count":{"$sum":1}}},
            #     {"$sort":{"count":-1}},
            #     {"$limit":1}
            # ])
            # print(record_aggregate)

            ## Use aggregate to get 10 effects
            # for doc in estimates.aggregate([
            #     {'$match': {'estimates.rxnorm': '19097016'}}, 
            #     {'$group': {'_id': '$estimates.snomed', 'snomed_count': {'$sum': 1}}}, 
            #     {"$sort":{"count":-1}},
            #     {"$limit":10}
            # ]):
            # print(doc)

            ## This does not print out correctly
            ## Consider using this: https://stackoverflow.com/questions/8782136/how-to-log-pymongo-queries
            #print >> sys.stderr, "%s" % record_aggregate

            ## Now set aggregate to results and iterate
            # results = record_aggregate
            # count = 1
            
            # for result in results:
            #     json_return.append({
            #         "effect": str(result['pt']),
            #         "rank": int(count)
            #     })
            #     count++

            # Comment the next 6 lines out ... Uncomment out everything above
            # json_return.append({ 
            #     "effect_string" : "Example Effect",
            #     "effect_rank" : "10",
            #     "effect_snomed" : "435459",
            #     "effect_rxnorm" : "19097016"
            # })
        # print(json.dumps(json_return, indent=2))
        return json.dumps(json_return)

    elif service == 'druginfo':
        if method == 'jobIndexes':
            # query e.g.,: {'drugs': u'19097016'}
            drugs = [int(x)for x in query['drugs'].split(',')]
            drugs.sort()
            job_indexes = list()
            for d in drugs:
                single_drug = druginfo.find_one({'rxnorm': d})
                job_indexes.append(str(single_drug['run_index']))
            job_indexes.sort()
            job_index_string = '_'.join(job_indexes)
            json_return = {'job_indexes': job_indexes,
                           'job_index_string': job_index_string}
            return json.dumps(json_return)

    elif service == 'gpcr':
        if method == 'gpcrFromUniprot':
            # query e.g.,: {'uniprot': }
            all_gpcrs = list(gpcr.find({'GPCR_uniprot_': query['uniprot']}, 
                                       {'_id': 0, 'cell_line_ID': 0}))
            return json.dumps(all_gpcrs)

def query_nsides_in(function, request):
    client = connect()
    db = client.nsides_in
    return function(db, request)

def drugs_from_effect(effect):
    client = connect()
    db = client.nsides_in
    estimates = db.estimates

    num_results = 10000
    effect = int(effect)

    pipeline = [
        {"$match": {"snomed": effect}},
        {"$unwind": "$nreports"},
        {"$group": {"_id": "$rxnorm", "totalnreports": { "$sum": "$nreports.nreports" }} },
        {"$match": {"totalnreports": {"$gte": 1} } },  # $gte selects greater than or equal to 
        {"$sort": {"totalnreports": -1} },  # descending order
        {"$limit": num_results}
    ]

    estimate_records = estimates.aggregate(pipeline)
    # ipdb.set_trace()
    # print len(estimate_records)
    listOptions = []

    for record in estimate_records:
        rxnormId = record['_id']
        listOptions.append({
            'value': str(rxnormId),
            'label': mongodbRxnormToName[rxnormId]
        })
    print len(listOptions)
    
    return json.dumps({
                "topOutcomes" : listOptions,
                "effect" : effect,
            })

def effects_from_ingredients(drugs):
    client = connect()
    db = client.nsides_in
    estimates = db.estimates
    estimates_agave = db.estimates_agave
    num_results = 10000
    collection = None
    drugs = str(drugs)
    print 'params', drugs, len(drugs.split(',')), type(drugs), type(drugs) == 'string'

    if len(drugs.split(',')) == 1:
        drugs = int(drugs)
        collection = estimates
    else:
        drugs = str(drugs)
        collection = estimates_agave

    pipeline = [
        {"$match": {"rxnorm": drugs}},
        {"$unwind": "$nreports"},
        {"$group": {
            "_id": "$snomed", 
            "totalnreports": { "$sum": "$nreports.nreports" }
            }
        },
        {"$match": {"totalnreports": {"$gte": 1} } },  # $gte selects greater than or equal to 
        {"$sort": {"totalnreports": -1} },  # descending order
        {"$limit": num_results}
    ]

    estimate_records = collection.aggregate(pipeline)
    # ipdb.set_trace()

    outcomes = []
    estimate_records = list(estimate_records)

    if len(estimate_records) != 0:
        for record in estimate_records:
            # print record
            outcomes.append(str(record['_id']))
    else:
        return json.dumps({ 'topOutcomes': [] })

    concept_mappings = query_nsides_mysql.query_db(service='omop', method='conceptsToName',
                                                    query= ",".join(outcomes) )

    concept_id2name = dict()
    for m in concept_mappings:
        concept_id2name[ str(m['concept_id']) ] = m['concept_name']

    outcome_options = []
    for position, concept_id in enumerate(outcomes): # Added enumeration to list
        if concept_id in concept_id2name:
            outcome_options.append( { 'value': concept_id, 'label': str(position + 1) + " - " + concept_id2name[concept_id].replace("'", "") } )
        else:
            print "could not find", concept_id

    return json.dumps({
            "topOutcomes" : outcome_options,
            "drug" : drugs,
            # "concept_mappings": concept_mappings
        })

def drugs_and_effect_result(db, request):
    drugs = str(request.args.get('drugs'))
    outcome = request.args.get('outcome')
    splitDrug = drugs.split(',')
    print drugs

    if len(splitDrug) == 1:
        collection = db.estimates
        drugs = int(drugs)
    else:
        collection = db.estimates_agave
        drugs = str(drugs)

    estimate_records = collection.find(
                        { '$and':
                            [ { 'rxnorm': drugs },
                            { 'snomed': int(outcome) }
                            ]
                        })

    results = { 'results': []}
    estimate_records = list(estimate_records)
    if len(estimate_records) == 0:
        print "  No record found"
    else:
        for estimate_record in estimate_records:
            # Sort estimates by year and remove unicode from estimate keys
            sorted_estimates = sorted(estimate_record[u"estimates"], key=lambda k: k[u'year'])
            sorted_nreports = sorted(estimate_record[u"nreports"], key=lambda k: k[u'year'])

            model_type = estimate_record[u"model"]

            processed_estimates = []
            for s in sorted_estimates:
                processed_year_estimate = dict()
                for k in s.keys():
                    processed_year_estimate[k.encode('ascii','ignore')] = s[k]
                processed_estimates.append( processed_year_estimate )
            # print s.keys()
            # print estimate_record[u"estimates"], '\n'

            processed_nreports = []
            for r in sorted_nreports:
                nreport_for_year = dict()
                for k in r.keys():
                    nreport_for_year[k.encode('ascii', 'ignore')] = r[k]
                processed_nreports.append(nreport_for_year)

            # print "  ", processed_estimates
            # print "  ", sorted_nreports

            results['results'].append({ 
                "outcome" : int(estimate_record[u"snomed"]), #query["outcome"],
                "drug" : estimate_record[u"rxnorm"], #query["drugs"],
                "estimates": processed_estimates, #estimate_record[u"estimates"]
                "nreports": processed_nreports,
                "model": model_type
            })

    return json.dumps(results)



'''
Utility functions for creating dictionaries like mongodbRxnormToName (in nsides_helpers.py)
'''

def get_dictionary_of_all_ingredients_or_effects(ingredients_or_effect):
    client = connect()
    db = client.nsides_in
    estimates = db.estimates
    from_db = None
    # reference = None
    get_name = None

    if ingredients_or_effect == 'ingredients':
        # reference = allIngredientRxnormToName
        from_db = estimates.distinct('rxnorm')
        get_name = get_dict_convertRxnormToName # this will take longer because you're looking up an api each time
    elif ingredients_or_effect == 'effects':
        # reference = allEffectsSnomedToName
        from_db = estimates.distinct('snomed')
        get_name = get_dict_convertSnomedToName

    holder = {}
    get_name(from_db, holder)

    return json.dumps(holder)    

def get_dict_convertSnomedToName (from_db, holder):
    cursor = query_nsides_mysql.connect().cursor()
    total_snomed = []
    for snomed in from_db:
        total_snomed.append(snomed)

    tuple_snomed = tuple(total_snomed)
    cursor.execute('''
        SELECT concept_name, concept_id FROM concept WHERE
        concept_id in {}
    '''.format(tuple_snomed))
    data = cursor.fetchall()

    for item in data:
        print item
        holder[item['concept_id']] = item['concept_name']

def get_dict_convertRxnormToName (from_db, holder):
    name = None
    for item_id in from_db:
        str_item_id = str(item_id)
        if str_item_id in allIngredientRxnormToName:
            name = allIngredientRxnormToName[str_item_id]
            holder[item_id] = name
        else:
            url = urlopen('https://rxnav.nlm.nih.gov/REST/rxcui/' + str_item_id + '/properties.json')
            data = json.load(url) #loads the json object
            if data is not None:
                name = data["properties"]["name"]
                holder[item_id] = name
            else:
                print 'could not find', str_item_id
    # return name

def get_suggestions_of_all_ingredients_or_effects(request):
    client = connect()
    db = client.nsides_in
    collection = db.estimates

    ingredients_or_effect = request.args.get('type')
    id_code = request.args.get('id_code')

    target_id = None
    nameConversion = None
    suggestions = []
    pipeline = []

    if ingredients_or_effect == 'ingredients':
        target_id = '$rxnorm'
        match_type = 'snomed'
        nameConversion = get_suggestions_convertRxnormToName
    elif ingredients_or_effect == 'effects':
        target_id = '$snomed'
        match_type = 'rxnorm'
        nameConversion = get_suggestions_convertSnomedToName

    print match_type, id_code, type(id_code)

    if id_code != None:
        pipeline.insert(0, {"$match": { match_type : int(id_code) } })

    pipeline.extend([
        # {"$unwind": "$nreports"},
        {"$unwind": "$estimates"},
        {
            "$group": {
                "_id": target_id, 
                # "totalnreports": { "$sum": "$nreports.nreports" },
                "maximum_lower_bound": { 
                    "$max": {
                        "$subtract": ["$estimates.prr", "$estimates.ci"]
                    } 
                }
            }
        },
        # {"$match": {"totalnreports": {"$gte": 1} } },  # $gte selects greater than or equal to 
        {"$sort": {"maximum_lower_bound": -1} }
    ])
    estimate_records = collection.aggregate(pipeline)
    # ipdb.set_trace()
    estimate_records = list(estimate_records)
    print pipeline, estimate_records, len(estimate_records) 

    if len(estimate_records) == 0:
        return json.dumps({ 'topOutcomes': [] })
    
    ref = nameConversion(estimate_records, suggestions)

    return json.dumps({
        'suggests': suggestions,
        'ref': ref
    })


def get_suggestions_convertSnomedToName (from_db, list_item):
    cursor = query_nsides_mysql.connect().cursor()
    total_snomed = []
    for item in from_db:
        snomed = item['_id']
        total_snomed.append(snomed)
    
    tuple_snomed = tuple(total_snomed)
    cursor.execute('''
        SELECT concept_name, concept_id FROM concept WHERE
        concept_id in {}
        '''.format(tuple_snomed))
    data = cursor.fetchall()

    ref = {}

    for item in data:
        ref[item['concept_id']] = item['concept_name']

    for position, item in enumerate(from_db):
        snomed = item['_id']
        list_item.append({
            'value': str(snomed),
            'label': str(position + 1) + " - " + ref[snomed]
        })
    return ref

def get_suggestions_convertRxnormToName (from_db, list_item):
    for position, item in enumerate(from_db):
        item_id = item['_id']
        str_item_id = str(item_id)
        if str_item_id in allIngredientRxnormToName:
            name = allIngredientRxnormToName[str_item_id]
            # holder[item_id] = name
            list_item.append({
                'value': str_item_id,
                'label': str(position + 1) + " - " + name
            })
        else:
            url = urlopen('https://rxnav.nlm.nih.gov/REST/rxcui/' + str_item_id + '/properties.json')
            data = json.load(url) #loads the json object
            if data is not None:
                name = data["properties"]["name"]
                list_item.append({
                    'value': str_item_id,
                    'label': str(position + 1) + " - " + name
                })
            else:
                print 'could not find', str_item_id

def add_field_maximum_lower_bound():
    client = connect()
    db = client.nsides_in
    collection = db.estimates
    pipeline = [
        {'$match': {'snomed': 31967}},
        {"$unwind": "$estimates"},
        {
            "$group": {
                '_id': {
                    "rxnorm_id": '$rxnorm',
                    "snomed_id": '$snomed',
                    'model': '$model'
                },
                # "totalnreports": { "$sum": "$nreports.nreports" },
                "maximum_lower_bound": { 
                    "$max": {
                        "$subtract": ["$estimates.prr", "$estimates.ci"]
                    } 
                }
            }
    }]

    data = collection.aggregate(pipeline)

    full_writes = []
    for item in data:
        _id = item['_id']
        snomed_id = _id['snomed_id']
        rxnorm_id = _id['rxnorm_id']
        model = _id['model']
        maximum_lower_bound = item['maximum_lower_bound']
        # print item, snomed_id, rxnorm_id, type(maximum_lower_bound)

        write = UpdateOne({
                'snomed': snomed_id,
                'rxnorm': rxnorm_id,
                'model': model
            },
            {
                '$set': {
                    'maximum_lower_bound': maximum_lower_bound
                }
        })

        full_writes.append(write)

    print full_writes[0]
    collection.bulk_write(full_writes)

def sort_by_mlb():
    client = connect()
    db = client.nsides_in
    collection = db.estimates
    collection.aggregate([
        {'$match': {'snomed': 31967}},
        {'$sort': { 'maximum_lower_bound': -1}}
    ])
    print 'done'
# def convertNameToRxnorm (name):
#     url = urlopen('https://rxnav.nlm.nih.gov/REST/rxcui.json?name=' + name)
#     data = json.load(url)
#     return data['idGroup']['rxnormId']

# def makeIngredientReference (rxnormDrugs):
#     ref = {}
#     for drug in rxnormDrugs:
#         drug_name = drug['label']
#         drug_name = drug_name.replace(' ', '%20')

#         url = urlopen('https://rxnav.nlm.nih.gov/REST/rxcui.json?name=' + drug_name)  #get rxnormId from name
#         data = json.load(url)
        
#         rx_id = data['idGroup']['rxnormId']
#         ref[drug_name] = rx_id[0]
#     print ref

#264198 ms
#

if __name__ == '__main__':
    main()
