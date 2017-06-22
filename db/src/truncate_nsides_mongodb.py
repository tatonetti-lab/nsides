"""
truncate_nsides_mongodb.py

Drops the nsides mongodb

@author Nicholas Tatonetti, 2017

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

client = pymongo.MongoClient(MONGODB_HOST, MONGODB_PORT)
client.drop_database('nsides')