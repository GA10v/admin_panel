import logging
import time

from components import log_config, state
from components.settings import Settings
from data_transform import DataTransformer
from elastic_loader import ESLoader
from pg_extractor import PostgresExtractor

log_config.get_log()

def check_es_index() -> None:
    """Проверка наличия | создание индекса в Elasticsearch."""
    storage = state.JsonFileStorage(Settings().state_file)
    state_maneger = state.State(storage)
    loader = ESLoader(Settings().es_url, Settings().es_index, state_maneger)
    es_conn = loader.connection

    if not es_conn.indices.exists(index=Settings().es_index):
        logging.warning('Отсутствеут индекс в Elasticsearch')
        loader.push_index()
        logging.info('Создан новый индекс в Elasticsearch')

def main(time_to_sleep: int = 2, batch_size: int = 10) -> None:
    """Основная логика работы с Elasticsearch.

    Args:
        time_to_sleep: Время ожидания перед проверкой наличия обновлений в psql.
        batch_size: Количество данных, получаемых из psql за один запрос.
    """
    storage = state.JsonFileStorage(Settings().state_file)
    # storage = state.RedisStorage()
    state_maneger = state.State(storage)
    extractor = PostgresExtractor(dsl=Settings().dsl_pg, state_maneger=state_maneger, batch_size=batch_size)
    transformer = DataTransformer()
    loader = ESLoader(Settings().es_url, Settings().es_index, state_maneger)

    if pg_data := [item for item in extractor.get_data()]:
        bulk = transformer.compile_data(pg_data=pg_data)
        last_update_time = transformer.get_last_update_time()
        loader.push_bulk(bulk=bulk, last_update_time=last_update_time)
    else:
        time.sleep(time_to_sleep)


if __name__ == '__main__':
    check_es_index()
    while True:
        main()
