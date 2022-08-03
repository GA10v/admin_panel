import os

from pydantic import BaseSettings

from .models import DBConf, RedisConf


class Settings(BaseSettings):
    """Класс для хранения настроек для ETL."""
    pg_models: list = ['film_work', 'person', 'genre']
    redis_key: str = os.environ.get('REDIS_KEY')
    es_index: str = os.environ.get('ES_INDEX')
    es_url: str = os.environ.get('ES_URL')
    state_key: str = os.environ.get('STATE_KEY')
    state_file: str = os.environ.get('STATE_FILE')
    dsl_pg: DBConf = {
        'host': os.environ.get('DB_HOST'),
        'database': os.environ.get('DB_NAME'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'port': os.environ.get('DB_PORT'),
    }
    dsl_redis: RedisConf = {
        'host': os.environ.get('REDIS_HOST'),
        'port': int(os.environ.get('REDIS_PORT')),
        'db': os.environ.get('REDIS_DB'),
    }