import sqlite3
import os
from flask import current_app, g

DATABASE = 'database.db'

def get_db():
    if 'db' not in g:
        # Get the absolute path to the webcode directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, DATABASE)
        
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    
    # Get the absolute path to the schema file
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')
    
    with open(schema_path) as f:
        db.executescript(f.read())

def init_app(app):
    app.teardown_appcontext(close_db)

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv 