from pg_extractor import PostgresExtractor
from data_transform import DataTransformer
from elastic_loader import ESLoader
from components import log_config, state, constants
import time
import logging


def main(time_to_sleep: int = 2, batch_size: int = 10) -> None:
    log_config.get_log()
    storage = state.JsonFileStorage(constants.STATE_FILE)
    state_maneger = state.State(storage)
    extractor = PostgresExtractor(
        dsl=constants.DSL_PG, state_maneger=state_maneger, batch_size=batch_size)
    transformer = DataTransformer()
    loader = ESLoader(constants.ES_URL, constants.ES_INDEX, state_maneger)
    es_conn = loader.connection

    if not es_conn.indices.exists(index=constants.ES_INDEX):
        loader.push_index()

    pg_data = [x for x in extractor.get_data()]

    if pg_data:
        bulk = transformer.compile_data(pg_data=pg_data)
        last_update_time = transformer.get_last_update_time()
        loader.push_bulk(bulk=bulk, last_update_time=last_update_time)
    else:
        logging.info('Нет данных для загрузки в Elasticsearch')
        time.sleep(time_to_sleep)


if __name__ == '__main__':
    while True:
        main()
