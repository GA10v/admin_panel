import logging
from contextlib import contextmanager

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from components import log_config, models_pg
from functools import wraps
import time

log_config.get_log()


@contextmanager
def pg_conn_context(dsl: models_pg.DBConf, cursor_factory=DictCursor) -> _connection:
    """Контекстный менеджер для psql.

    Args:
        dsl: Данные для подключения к psql
        cursor_factory: Курсор

    Yields:
        _connection: Конектор
    """
    try:
        conn = psycopg2.connect(**dsl, cursor_factory=cursor_factory)
        yield conn
    except psycopg2.Error as er:
        logging.error(er)
        raise er
    finally:
        conn.close()


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка. Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time

    Args:
        start_sleep_time: Начальное время повтора
        factor: Во сколько раз нужно увеличить время ожидания
        border_sleep_time: Граничное время ожидания

    Returns: 
        func_wrapper: Результат выполнения функции
    """
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time = start_sleep_time
            n = 1
            while True:
                try:
                    return func(*args, **kwargs)
                # разобраться с исключениями
                except Exception as er:
                    logging.error(er)
                    time.sleep(sleep_time)
                    if sleep_time >= border_sleep_time:
                        sleep_time = border_sleep_time
                    else:
                        sleep_time = start_sleep_time * 2 ^ (n)
                        n *= factor
        return inner
    return func_wrapper
