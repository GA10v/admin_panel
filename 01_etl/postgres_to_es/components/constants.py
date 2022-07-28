import os

from dotenv import load_dotenv


load_dotenv()

PG_MODELS = ['filmwork', 'person', 'genre']

DSL_PG = {
    'host': os.environ.get('DB_HOST'),
    'database': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'port': os.environ.get('DB_PORT'),
}

