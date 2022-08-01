import logging

from components import log_config
from functools import wraps
import time

log_config.get_log()


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
