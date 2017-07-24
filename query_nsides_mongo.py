"""
populate_nsides_mongodb.py

Connects to MongoDB and extracts records for API's usage

@author Victor Nwankwo, 2017
@author Tal Lorberbaum, 2017

USAGE:

Ensure that nsides-mongo.cnf file exists


"""

# import os
import sys
# import numpy
# import pickle
# import shutil
# import tarfile
import pymongo
# from bson.code import Code # for some this needs to be pymongo.bson

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
    
    print >> sys.stderr, "Reading the 'nsides' mongodb at %s:%s" % (MONGODB_HOST, MONGODB_PORT)
    
    client = pymongo.MongoClient('mongodb://%s:%s@%s:%s/admin' % (MONGODB_UN, MONGODB_PW, MONGODB_HOST, MONGODB_PORT))
    db = client.nsides
    estimates = db.estimates

    print >> sys.stderr, "%s" % db.collection_names()
    print >> sys.stderr, "%s" % str(estimates.count())

    record_by_find = estimates.find_one({"rxnorm": "19097016"})
    record_by_id = estimates.find_one({"_id": "595fe5316246306dc7d048e2"})

    return True

def query_db(service, method, query=False, cache=False):

    print "Connecting to the API..."

    # Connect to MongoDB database
    print "Connecting to database"

    print >> sys.stderr, "Loading password from ./nsides-mongo.cnf..."
    MONGODB_HOST, MONGODB_UN, MONGODB_PW = open('./nsides-mongo.cnf').read().strip().split('\n')
    
    print >> sys.stderr, "Reading the 'nsides' mongodb at %s:%s" % (MONGODB_HOST, MONGODB_PORT)
    
    client = pymongo.MongoClient('mongodb://%s:%s@%s:%s/admin' % (MONGODB_UN, MONGODB_PW, MONGODB_HOST, MONGODB_PORT))
    db = client.nsides
    estimates = db.estimates

    json_return = []
    if service == 'nsides':
        print "Service: ",service
        print "Method: ", method
        print "Query : ", query
        if method == 'top10Effects': #'get_top_10_effects':
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
            json_return.append({ 
                "effect_string" : "Example Effect",
                "effect_rank" : "10",
                "effect_snomed" : "435459",
                "effect_rxnorm" : "19097016"
            }) 
        return json_return

if __name__ == '__main__':
    main()
