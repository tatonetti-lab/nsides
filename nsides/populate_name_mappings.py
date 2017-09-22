from __future__ import print_function

import requests
import numpy as np
import pymongo
import json
import os, sys

MONGODB_HOST, MONGODB_UN, MONGODB_PW = open('../nsides-mongo.cnf').read().strip().split('\n')
MONGODB_PORT = 27017

RXNORM_BASE = 'https://rxnav.nlm.nih.gov/REST/rxcui'

rxcuimap = np.load('concept2rxnorm.npy').flatten()[0]

client = pymongo.MongoClient('mongodb://%s:%s@%s:%s/admin' % (MONGODB_UN, MONGODB_PW, MONGODB_HOST, MONGODB_PORT))
db = client.nsides
druginfo = db.druginfo

def get_string_name(rxcui):
    res = requests.get(RXNORM_BASE + '/{0}/property.json?propName=RxNorm%20Name'.format(rxcui))
    x = json.loads(res.text)
    try:
        try:
            ret = x['propConceptGroup']['propConcept'][0]['propValue']
        except TypeError:
            return None
        return ret
    except KeyError:
        return None

for k, v in rxcuimap.iteritems():
    name = get_string_name(int(v))
    print("{0}: {1}".format(k, name))
    druginfo.update_one({'rxnorm': int(k)},
                        {'$set': {"name": name}},
                        upsert=False)
