import psycopg2
from flask import g

from utils.config import config
from utils.server import app

db_url = config.get('db', 'url')


def connect_to_db():
    return psycopg2.connect(db_url)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_db()
    return db


@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
