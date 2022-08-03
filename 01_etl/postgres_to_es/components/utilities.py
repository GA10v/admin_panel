import logging
import time
from functools import wraps

import elasticsearch
import psycopg2
import redis

from components import log_config


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10, max_repeat=10, logger=log_config.get_log):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.

    Использует наивный экспоненциальный рост времени повтора (factor)

    до граничного времени ожидания (border_sleep_time).

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time

    Args:
        start_sleep_time: Начальное время повтора.
        factor: Во сколько раз нужно увеличить время ожидания.
        border_sleep_time: Граничное время ожидания.
        max_repeat: Максимальное количество вызовов декоратора backoff.
        logger: Логгер.

    Returns:
        func_wrapper: Результат выполнения функции.
    """
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            logger()
            count = 0
            sleep_time = start_sleep_time
            n = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except (psycopg2.OperationalError, elasticsearch.TransportError, redis.exceptions.ConnectionError) as er:
                    count += 1
                    logging.error(er)
                    time.sleep(sleep_time)
                    if sleep_time >= border_sleep_time:
                        sleep_time = border_sleep_time
                    else:
                        sleep_time = start_sleep_time * 2 ^ (n)
                        n *= factor
                finally:
                    if count > max_repeat:
                        logging.error('Превышено количество вызовов декоратора backoff')
                        raise RuntimeError('Превышено количество вызовов декоратора backoff')
        return inner
    return func_wrapper
