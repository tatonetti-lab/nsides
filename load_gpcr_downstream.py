import pandas as pd
import pymongo
from tqdm import tqdm

x = pd.read_csv("GPCR_downstream_pathway.txt", sep="\t", dtype=object)

xd = x.to_dict('records')

MONGODB_PORT = 27017
MONGODB_HOST, MONGODB_UN, MONGODB_PW = open('./nsides/nsides-mongo.cnf').read().strip().split('\n')
client = pymongo.MongoClient('mongodb://%s:%s@%s:%s/nsides_dev?authSource=admin' % (MONGODB_UN, MONGODB_PW, MONGODB_HOST, MONGODB_PORT))

nsides_dev = client.nsides_dev
gpcr = nsides_dev.gpcr

for g in tqdm(xd):
    gpcr.insert_one(g)