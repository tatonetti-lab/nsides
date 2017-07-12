"""
populate_nsides_mongodb.py

Connects to MongoDB and extracts records for API's usage

@author Victor Nwankwo, 2017

USAGE:

Ensure that nsides-mongo.cnf file exists


"""

import os
import sys
import numpy
import pickle
import shutil
import tarfile
import pymongo

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
    
    client = pymongo.MongoClient('mongodb://%s:%s@%s:%s/nsides' % (MONGODB_UN, MONGODB_PW, MONGODB_HOST, MONGODB_PORT))
    db = client.nsides
    estimates = db.estimates

    print >> estimates.count()

    record_by_find = estimates.find_one({"rxnorm": "19097016"})
    record_by_id = estimates.find_one({"_id": "595fe5316246306dc7d048e2"})
    # Querying for More Than One Document
    # for estimate in estimates.find({"rxnorm": "19097016"}):
    #     print >> estimate
    
    return True

if __name__ == '__main__':
    main()