"""Manage access to the database."""

import sqlite3
from flask import g,jsonify
from pymongo import MongoClient
import json
from bson import BSON
from bson import json_util
from bson.objectid import ObjectId

# sqlite3 example
class Database:
    """Database access."""

    def __init__(self, app):
        """Constructor."""
        self.app = app

        @app.teardown_appcontext
        def close_connection(exception):
            """Close database connection when finished handling request."""
            db = getattr(g, '_database', None)

            if db is not None:
                db.close()

    def connect_to_db(self):
        """Open database and return a connection handle."""
        return sqlite3.connect(self.app.config['DATABASE'])

    def get_db(self):
        """Return the app global db connection or create one."""
        db = getattr(g, '_database', None)

        if db is None:
            db = g._database = self.connect_to_db()
            db.row_factory = sqlite3.Row

        return db

    def query_db(self, query, args=(), one=False):
        """Query the database."""
        cur = self.get_db().execute(query, args)

        rv = cur.fetchall()
        cur.close()

        return (rv[0] if rv else None) if one else rv

    def save_profile(self,
                     identity_id=None,
                     name=None,
                     email=None,
                     institution=None):
        """Persist user profile."""
        db = self.get_db()

        db.execute("""update profile set name = ?, email = ?, institution = ?
                   where identity_id = ?""",
                   (name, email, institution, identity_id))

        db.execute("""insert into profile (identity_id, name, email, institution)
                   select ?, ?, ?, ? where changes() = 0""",
                   (identity_id, name, email, institution))
        db.commit()

    def load_profile(self, identity_id):
        """Load user profile."""
        return self.query_db("""select name, email, institution from profile
                             where identity_id = ?""",
                             [identity_id],
                             one=True)

# mongodb example
class MongoConnection():
    def __init__ (self, app):
        self.app = app
        self.client = MongoClient('localhost:27017')
        self.db = self.client.nsides_db

    def get_one(self,table_name,conditions={}):
        single_doc = self.db[table_name].find_one(conditions)
        json_doc = json.dumps(single_doc,default=json_util.default)
        json_doc = json_doc.replace("$oid", "id")
        json_doc = json_doc.replace("_id", "uid")
        return json.loads(json_doc)

    def get_all(self,table_name,conditions={}, sort_index ='_id', limit=100):
        all_doc = self.db[table_name].find(conditions).sort(sort_index, pymongo.DESCENDING).limit(limit)
        json_doc = json.dumps(list(all_doc),default=json_util.default)
        json_doc = json_doc.replace("$oid", "id")
        json_doc = json_doc.replace("_id", "uid")
        return json.loads(str(json_doc))

    def insert_one(self, table_name, value):
        try:
            self.db[table_name].insert_one(value)
            return jsonify(status='OK', message='inserted successfully')
        except Exception, e:
            return jsonify(status='ERROR', message=str(e))

    def update_one(self, table_name, where, what):
        try:
            # 'where' means {'_id':ObjectId(machineId)}
            self.db[table_name].update_one(where,{"$set":what},upsert=False)
            return jsonify(status='OK', message='updated successfully')
        except Exception, e:
            return jsonify(status='ERROR', message=str(e))

