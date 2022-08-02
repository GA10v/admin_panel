import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PG_MODELS = ['film_work', 'person', 'genre']

REDIS_KEY = os.environ.get('REDIS_KEY')

ES_INDEX = os.environ.get('ES_INDEX')

ES_URL = os.environ.get('ES_URL')

STATE_KEY = os.environ.get('STATE_KEY')

STATE_FILE = f'{Path(__file__).parent.parent}/data/last_state.json'

DSL_PG = {
    'host': os.environ.get('DB_HOST'),
    'database': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'port': os.environ.get('DB_PORT'),
}

DSL_ES = {
    'host': os.environ.get('ES_HOST'),
    'port': os.environ.get('ES_PORT'),
    'index': os.environ.get('ES_INDEX'),
}

DSL_REDIS = {
    'host': os.environ.get('REDIS_HOST'),
    'port': int(os.environ.get('REDIS_PORT')),
    'db': os.environ.get('REDIS_DB'),
}
