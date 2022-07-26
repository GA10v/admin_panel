import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from components import log_config, models_pg

log_config.get_log()


@contextmanager
def sqlite_conn_context(db_path: str) -> sqlite3.Connection:
    """Контекстный менеджер для sqlite3.

    Args:
        db_path: Путь к файлу db.sqlite
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        yield conn
    except Exception as er:
        logging.error(er)
    finally:
        conn.close()


@contextmanager
def pg_conn_context(dsl: models_pg.DBConf, cursor_factory=DictCursor) -> _connection:
    """Контекстный менеджер для psql.

    Args:
        dsl: Данные для подключения к psql
        cursor_factory: Курсор
    """
    try:
        conn = psycopg2.connect(**dsl, cursor_factory=cursor_factory)
        yield conn
    except psycopg2.Error as er:
        logging.error(er)
        raise er
    finally:
        conn.close()


def check_pg_models(dsl: models_pg.DBConf, ddl_path: str = f'{Path(__file__).parent.parent}/new_movies_database.ddl') -> bool:
    """Функция проверки наличия схемы БД для 3-го модуля.

    Args:
        dsl: Данные для подключения к pg
        ddl_path: Путь к файлу с настройками БД
    """
    with pg_conn_context(dsl) as pg_conn:
        with pg_conn.cursor() as cursor:
            table_names = {
                'film_work',
                'person',
                'genre',
                'person_film_work',
                'genre_film_work',
            }
            try:
                cursor.execute("SELECT table_name \
                                FROM information_schema.tables \
                                WHERE table_schema = 'content';")
                                
                if not table_names.issubset(set([colum[0] for colum in cursor])):

                    logging.warning('Схема content не соответствует db.sqlite')
                    logging.info('Запуск миграции данных из db.sqlite')

                    with open(ddl_path, 'r') as f:
                        cursor.execute(f.read())
                        pg_conn.commit()
                    return True

                cursor.execute("SELECT COUNT(id) FROM content.film_work;")                                
                if [_[0] for _ in cursor][0] < 999 :
                    logging.warning('Количество записей в "movies_database" не соответствует db.sqlite')
                    logging.info('Запуск миграции данных из db.sqlite')
                    return True
                else:
                    logging.info('БД "movies_database" соответствует db.sqlite')
                    return False
            except (FileNotFoundError, psycopg2.OperationalError) as er:
                logging.error(er)
