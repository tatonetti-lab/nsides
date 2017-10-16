import pymongo
import numpy as np
import pickle
import shutil
import tarfile
import os

EXTRACTED_DIR = './extracted'
REFERNCE_DIR = './reference'
RESULT_DIR = './result_data'

MONGODB_HOST = 'localhost'
MONGODB_UN = 'test'
MONGODB_PW = 'test'
MONGODB_PORT = 27017

client = pymongo.MongoClient('mongodb://%s:%s@%s:%s/nsides?authSource=admin'
                             % (MONGODB_UN, MONGODB_PW, MONGODB_HOST, MONGODB_PORT))
db = client.nsides_dev
estimates = db.test

outcomes = np.load(os.path.join(REFERNCE_DIR, 'all_outcome_strings.npy')) # snomed ids
drugs = np.load(os.path.join(REFERNCE_DIR, 'drug_strings.npy')) # rxnorm ids

if os.path.exists(EXTRACTED_DIR):
    shutil.rmtree(EXTRACTED_DIR)
os.mkdir(EXTRACTED_DIR)

OUTPUT_FILES = ['results_2451_dnn.tgz','results_2451_nopsm.tgz','results_2451_lrc.tgz']
OUTPUT_FILES_1 = ['results_2451_2001_dnn.tgz','results_2451_2001_nopsm.tgz','results_2451_2001_lrc.tgz']

for file in OUTPUT_FILES:
    tar = tarfile.open(os.path.join(RESULT_DIR,file))
    tar.extractall(path=EXTRACTED_DIR)

def partition(dnn, nopsm, lrc, nreports, iterable):
    dnn_files = []
    nopsm_files = []
    lrc_files = []
    nreports_files = []
    for item in iterable:
        if nreports(item):
            nreports_files.append(item)
        elif dnn(item):
            dnn_files.append(item)
        elif nopsm(item):
            nopsm_files.append(item)
        elif lrc(item):
            lrc_files.append(item)
    return dnn_files, nopsm_files, lrc_files, nreports_files
                                            
r_dnn,r_nopsm,r_lrc,r_nreports = partition(lambda x: x.startswith('results_dnn'),
                                           lambda x: x.startswith('results_nopsm'),
                                           lambda x: x.startswith('results_lrc'),
                                           lambda x: x.startswith('results_nreports'),
                                           os.listdir(EXTRACTED_DIR))
# print sorted(r_dnn)
# print sorted(r_nopsm)
# print sorted(r_lrc)
# print sorted(r_nreports)

document = dict()

drug_ind = OUTPUT_FILES[0].split('_')[1:-1]
drug_ind = [int(x) for x in drug_ind]
rxnorm = [drugs[x] for x in drug_ind]

concat_rxnorm = ''
for x in sorted(rxnorm):
    concat_rxnorm = concat_rxnorm + str(x) + ','
concat_rxnorm = concat_rxnorm[:-1]
# print 'rxnorm',drug_ind,concat_rxnorm

def generate_data(model,year,obj,obj_N):
    for outcome_index in range(obj.shape[1]):
        prr = obj[0,outcome_index]
        ci = obj[1,outcome_index]

        nreports = obj_N[0,outcome_index]

        if np.isnan(prr) or np.isnan(ci):
            prr = -1
            ci = -1

        snomed = outcomes[outcome_index]
        key = (str(concat_rxnorm),str(snomed),model)

        if not key in document:
            doc = dict()
            doc['rxnorm'] = concat_rxnorm
            doc['snomed'] = snomed
            doc['model'] = model
            doc['estimates'] = list()
            doc['nreports'] = list()
            document[key] = doc

        doc = document[key]
        doc['estimates'].append({'year': year, 'prr': prr, 'ci': ci})
        doc['nreports'].append({'year': year, 'nreports':nreports})

for item in zip(sorted(r_dnn),sorted(r_nopsm),sorted(r_lrc),sorted(r_nreports)):
    year = int(item[0].split('_')[-1].split('.')[0])
    print 'yeay',year, 'item',item
    f_nreports = open(os.path.join(EXTRACTED_DIR,item[3]))
    nreports_obj = pickle.load(f_nreports)

    f_dnn = open(os.path.join(EXTRACTED_DIR,item[0]))
    dnn_obj = pickle.load(f_dnn)
    generate_data('dnn',year,dnn_obj,nreports_obj)
    
    f_nopsm = open(os.path.join(EXTRACTED_DIR,item[1]))
    nopsm_obj = pickle.load(f_nopsm)
    generate_data('nopsm',year,dnn_obj,nreports_obj)

    f_lrc = open(os.path.join(EXTRACTED_DIR,item[2]))
    lrc_obj = pickle.load(f_lrc)
    generate_data('lrc',year,dnn_obj,nreports_obj)

# for k in document.keys():
#     print k,document[k]
#     break

if len(document) != 0:
    estimates.insert_many(document.values())
