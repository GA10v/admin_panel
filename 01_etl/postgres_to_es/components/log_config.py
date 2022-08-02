import logging
from datetime import date
from pathlib import Path


def get_log() -> logging.basicConfig:
    """Функция логгирования.

    Returns:
        logging.basicConfig: Настройки для logging
    """
    log_conf = {
        'filename': f'{Path(__file__).parent.parent}/logs/load_data_{date.today()}.log',
        'filemode': 'a',
        'level': logging.INFO,
        'format': '%(asctime)s.%(msecs)03d [%(levelname)s] %(filename)s - %(funcName)s() : %(message)s',
        'datefmt': '%d/%m/%Y %H:%M:%S',
    }
    return logging.basicConfig(**log_conf)
