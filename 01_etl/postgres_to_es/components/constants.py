import os

from dotenv import load_dotenv


load_dotenv()

PG_MODELS = ['film_work', 'person', 'genre']

ES_INDEX = os.environ.get('ES_INDEX')

DSL_PG = {
    'host': os.environ.get('DB_HOST'),
    'database': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'port': os.environ.get('DB_PORT'),
}
