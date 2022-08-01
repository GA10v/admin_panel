from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk as _bulk
import logging
from components import log_config, state, constants, schema, utilities, models
from pg_extractor import PostgresExtractor
from data_transform import DataTransformer
from components.state import State

log_config.get_log()


class ESLoader:
    def __init__(self, connection: Elasticsearch, index_name: str, state_maneger: State):
        """
        Args:
            connection: Клиент для связи с сервером Elasticsearch.
            index_name: Индекс.
            state_maneger: Объект класса State для хранения состояний.
        """
        self.connection = connection
        self.index_name = index_name
        self.state_maneger = state_maneger

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
            _bulk(self.connection, actions=bulk, index=self.index_name)
            self.state_maneger.set_state(
                key=constants.STATE_KEY, value=last_update_time)
        except Exception as er:
            logging.error(er)
            raise er


if __name__ == '__main__':
    storage = state.JsonFileStorage(constants.STATE_FILE)
    state_maneger = state.State(storage)
    es_conn = Elasticsearch(constants.ES_URL)
    transformer = DataTransformer()
    loader = ESLoader(es_conn, constants.ES_INDEX, state_maneger)
    
    if not es_conn.indices.exists(index=constants.ES_INDEX):
        loader.push_index()

    with utilities.pg_conn_context(constants.DSL_PG) as pg_conn:
        extractor = PostgresExtractor(connection=pg_conn, state_maneger=state_maneger, batch_size=100)
        pg_data = [x for x in extractor.get_data()]
        if pg_data:
            bulk = transformer.compile_data(pg_data=pg_data)
            print(bulk)
            last_update_time = transformer.last_update_time
            loader.push_bulk(bulk=bulk, last_update_time=last_update_time)
        else:
            print('no data')
