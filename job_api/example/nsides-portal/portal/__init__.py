from flask import Flask
import json

from portal.database import Database, MongoConnection

app = Flask(__name__)
app.config.from_pyfile('portal.conf')

database = Database(app)
mongodb = MongoConnection(app)

with open(app.config['JOB_TEMPLATE']) as f:
    jobtemplate = json.load(f)

import portal.views
