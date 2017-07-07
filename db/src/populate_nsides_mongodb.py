"""
populate_nsides_mongodb.py

Populates the nsides mongodb from the provided tar archived file.

@author Nicholas Tatonetti, 2017

USAGE:

If you want to instantiate this on a remote server that doesn't allow connections over 27017 then you
can open up an SSH tunnel, e.g.

ssh -L 27017:localhost:27017 username@removeserver.org


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

def main(archive_file):
    
    print >> sys.stderr, "Loading password from ../nsides-mongo-config.txt..."
    MONGODB_HOST, MONGODB_UN, MONGODB_PW = open('../nsides-mongo-config.txt').read().strip().split('\n')
    
    print >> sys.stderr, "Loading the reference data for drugs and outcomes..."
    outcomes = numpy.load(os.path.join(REFERNCE_DIR, 'all_outcome_strings.npy')) # snomed ids
    drugs = numpy.load(os.path.join(REFERNCE_DIR, 'drug_strings.npy')) # rxnorm ids
    
    print >> sys.stderr, "Cleaning up extracted directory..."
    shutil.rmtree(EXTRACTED_DIR)
    os.mkdir(EXTRACTED_DIR)
    
    print >> sys.stderr, "Extracting %s to %s..." % (archive_file, EXTRACTED_DIR)
    tar = tarfile.open(archive_file)
    tar.extractall(path=EXTRACTED_DIR)
    
    resultsfiles = filter(lambda x: x.startswith('results'), os.listdir(EXTRACTED_DIR))
    
    print >> sys.stderr, "Found %d results files." % len(resultsfiles)
    
    print >> sys.stderr, "Processing data files.."
    
    documents = dict()
    
    for rf in resultsfiles:
        
        if rf.startswith('results_nreports'):
            # we can't handle this right now
            continue
        
        f = open(os.path.join(EXTRACTED_DIR, rf))
        obj = pickle.load(f)
        
        year = int(rf.split('_')[-1].split('.')[0])
        model = rf.split('_')[1]
        drug_index = int(rf.split('_')[2])
        
        #print drugs[drug_index], model, year, obj.shape
        
        for outcome_index in range(obj.shape[1]):
            
            prr = obj[0,outcome_index]
            ci = obj[1,outcome_index]
            
            if numpy.isnan(prr) or numpy.isnan(ci):
                continue
            
            rxnorm = drugs[drug_index]
            snomed = outcomes[outcome_index]
            
            key = (rxnorm, snomed, model)
            
            if not key in documents:
                doc = dict()
                doc['rxnorm'] = rxnorm
                doc['snomed'] = snomed
                doc['model'] = model
                doc['estimates'] = list()
                doc['nreports'] = 0
                documents[key] = doc
            
            doc = documents[key]
            doc['estimates'].append({'year': year, 'prr': prr, 'ci': ci})
    
    print >> sys.stderr, "Fishined processing, created %d documents." % len(documents)
    
    if len(documents) == 0:
        print >> sys.stderr, "No documents to save. Finished"
        return False
    
    print >> sys.stderr, "Loading data into the 'nsides' database in mongo at %s:%s" % (MONGODB_HOST, MONGODB_PORT)
    
    client = pymongo.MongoClient('mongodb://%s:%s@%s:%s/nsides' % (MONGODB_UN, MONGODB_PW, MONGODB_HOST, MONGODB_PORT))
    db = client.nsides
    estimates = db.estimates
    
    r = estimates.insert_many(documents.values())
    
    print >> sys.stderr, "Completed %d inserts." % len(r.inserted_ids)
    
    return True

if __name__ == '__main__':
    main(sys.argv[1])