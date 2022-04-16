import os
from os.path import join, dirname
from dotenv import load_dotenv
from datetime import datetime


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

sqlite_db = 'db.sqlite'

pg_dsl = {
    'dbname': os.environ.get('POSTGRES_DB'),
    'user': os.environ.get('POSTGRES_USER'),
    'password': os.environ.get('POSTGRES_PASSWORD'),
    'host': os.environ.get('POSTGRES_HOST', '127.0.0.1'),
    'port': os.environ.get('POSTGRES_PORT', 5432),
    'options': '-c search_path=public,content',
}

es_dsl = {
    'hosts': ['localhost'],
    'http_auth': (
        os.environ.get('ELASTIC_USER'),
        os.environ.get('ELASTIC_PASSWORD')
    )
}

LocalStorage = join(dirname(__file__), 'storage.json')

batch_limit = 10
initial_state = datetime.min
