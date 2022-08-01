from elasticsearch import Elasticsearch
import logging
from components import log_config, state, constants, schema, models
from pg_extractor import PostgresExtractor
from data_transform import DataTransformer
from components.state import State
from components.utilities import backoff

log_config.get_log()


class ESLoader:
    def __init__(self, dsl: str, index_name: str, state_maneger: State):
        """
        Args:
            dsl: Клиент для связи с сервером Elasticsearch.
            index_name: Индекс.
            state_maneger: Объект класса State для хранения состояний.
        """
        self.dsl = dsl
        self.index_name = index_name
        self.state_maneger = state_maneger
        self.connection = self.get_connection()

    @backoff()
    def get_connection(self) -> Elasticsearch:
        """ Реализация отказоустойчивости.

        Returns:
            Elasticsearch: Объект класса Elasticsearch, конектор.      
        """
        return Elasticsearch(self.dsl)

    @backoff()
    def check_connection(self) -> None:
        """Проверка связи с сервером Elasticsearch."""

        if not self.connection.ping():
            logging.error('Нет связи с сервером Elasticsearch')
            raise

    def push_index(self) -> None:
        """Отправка индекса в Elasticsearch."""

        body = schema.ES_SCHEMA
        try:
            self.check_connection()
            self.connection.indices.create(index=self.index_name, body=body)
        except Exception as er:
            logging.error(er)

    def push_bulk(self, bulk: list[models.ESDataConf], last_update_time: str) -> None:
        """
        Отправка пачки данных в Elasticsearch.

        Args:
            bulk: Список словарей для загрузки в Elasticserch.
            last_update_time: Время последнего обновления данных.
        """

        try:
            self.check_connection()
            self.connection.bulk(operations=bulk, index=self.index_name)
            logging.info('Данные успешно обновлены')
            self.state_maneger.set_state(
                key=constants.STATE_KEY, value=last_update_time)
            logging.info(f'Дата последнего обновления данных: {last_update_time}')
        except Exception as er:
            logging.error(er)


if __name__ == '__main__':
    storage = state.JsonFileStorage(constants.STATE_FILE)
    state_maneger = state.State(storage)
    es_conn = Elasticsearch(constants.ES_URL)
    transformer = DataTransformer()
    loader = ESLoader(constants.ES_URL, constants.ES_INDEX, state_maneger)
    es_conn = loader.connection

    if not es_conn.indices.exists(index=constants.ES_INDEX):
        loader.push_index()

    extractor = PostgresExtractor(dsl=constants.DSL_PG, state_maneger=state_maneger, batch_size=100)
    pg_data = [x for x in extractor.get_data()]
    if pg_data:
        bulk = transformer.compile_data(pg_data=pg_data)
        last_update_time = transformer.last_update_time
        print(last_update_time)
        loader.push_bulk(bulk=bulk, last_update_time=last_update_time)
    else:
        print('no data')
