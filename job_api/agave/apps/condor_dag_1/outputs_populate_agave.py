import pymongo
import numpy as np
import pickle
import shutil
import tarfile
import os

import argparse

parser = argparse.ArgumentParser(description='Populate the job output into the database')

parser.add_argument('--file-list',
                    help='file list for job outputs',
                    action='store',
                    default='',
                    dest='file_list')

args = parser.parse_args()

OUTPUT_FILES = args.file_list.split('\n')
print 'output files', OUTPUT_FILES

EXTRACTED_DIR = './extracted'
REFERNCE_DIR = './reference'

# MONGODB_HOST = '34.197.121.158'
# MONGODB_UN = 'cyoun'
# MONGODB_PW = 'test123'
MONGODB_HOST, MONGODB_UN, MONGODB_PW = open('./nsides-mongo-config.txt').read().strip().split('\n')
# print MONGODB_HOST, MONGODB_UN, MONGODB_PW
MONGODB_PORT = 27017

client = pymongo.MongoClient('mongodb://%s:%s@%s:%s/nsides?authSource=admin'
                             % (MONGODB_UN, MONGODB_PW, MONGODB_HOST, MONGODB_PORT))
db = client.nsides_dev
estimates = db.estimates

outcomes = np.load(os.path.join(REFERNCE_DIR, 'all_outcome_strings.npy')) # snomed ids
drugs = np.load(os.path.join(REFERNCE_DIR, 'unique_ingredients.npy')) # rxnorm ids

if os.path.exists(EXTRACTED_DIR):
    shutil.rmtree(EXTRACTED_DIR)
os.mkdir(EXTRACTED_DIR)

# OUTPUT_FILES = ['results_2451_dnn.tgz','results_2451_nopsm.tgz','results_2451_lrc.tgz']
# OUTPUT_FILES_1 = ['results_2451_2001_dnn.tgz','results_2451_2001_nopsm.tgz','results_2451_2001_lrc.tgz']

for file in OUTPUT_FILES:
    try:
        tar = tarfile.open(file,'r:gz')
        tar.extractall(path=EXTRACTED_DIR)
    except:
        print "Couldn't open tar file, exiting"
        quit()

document = dict()

drug_ind = OUTPUT_FILES[0].split('_')[1:-1]
print 'drug_ind 1', drug_ind

model = '_'.join(drug_ind)
print 'model', model

drug_ind = [int(x) for x in drug_ind]
print 'drug_ind 2', drug_ind
rxnorm = [drugs[x] for x in drug_ind]

concat_rxnorm = ''
for x in sorted(rxnorm):
    concat_rxnorm = concat_rxnorm + str(x) + ','
concat_rxnorm = concat_rxnorm[:-1]
print 'rxnorm',drug_ind,concat_rxnorm

for modeltype in ('dnn','nopsm','lrc'):

    num_files = len(filter(lambda x: ('results_%s' % modeltype in x) & x.endswith('.pkl'),[os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(EXTRACTED_DIR)) for f in fn]))
    if num_files!=13:
        print "Files are missing, exiting"
        quit()
    
    for year in range(2004,2017):
        fname = EXTRACTED_DIR+'/results_'+str(modeltype)+'_'+str(model)+'_'+str(year)+'.pkl'
        f = open(fname)
        obj = pickle.load(f)
        fname_N = EXTRACTED_DIR+'/results_nreports_nopsm_'+str(model)+'_'+str(year)+'.pkl'
        try:
            f_N = open(fname_N)
        except:
            print "Could not open ",fname_N
            continue
        obj_N = pickle.load(f_N)
    
        for outcome_index in range(obj.shape[1]):
            prr = obj[0,outcome_index]
            ci = obj[1,outcome_index]
    
            nreports = obj_N[0,outcome_index]
            
            if np.isnan(prr) or np.isnan(ci):
                prr = -1
                ci = -1
    
            snomed = outcomes[outcome_index]
    
            key = (str(concat_rxnorm),str(snomed),modeltype)
            
            if snomed == None:
                continue
    
            doc = dict()
            doc['rxnorm'] = concat_rxnorm
            doc['snomed'] = int(snomed)
            doc['model'] = str(modeltype)
            if year == 2004:
                doc['estimates'] = list()
                doc['nreports'] = list()
                doc['estimates'].append({'year': year, 'prr': prr, 'ci': ci})
                doc['nreports'].append({'year': year, 'nreports':nreports})
                document[key] = doc
            else:
                doc = document[key]
                doc['estimates'].append({'year': year, 'prr': prr, 'ci': ci})
                doc['nreports'].append({'year': year, 'nreports':nreports})

if os.path.exists(EXTRACTED_DIR):
    shutil.rmtree(EXTRACTED_DIR)

if len(document) != 0:
    print 'output data is being populated into MongoDB'
    estimates.insert_many(document.values())

