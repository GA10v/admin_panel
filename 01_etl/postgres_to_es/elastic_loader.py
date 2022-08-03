import logging

from elasticsearch import Elasticsearch, TransportError

from components import log_config, models, schema
from components.settings import Settings
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

    @backoff(logger=log_config.get_log)
    def get_connection(self) -> Elasticsearch:
        """ Реализация отказоустойчивости.

        Returns:
            Elasticsearch: Объект класса Elasticsearch, конектор.
        """
        return Elasticsearch(self.dsl)

    @backoff(logger=log_config.get_log)
    def check_connection(self) -> None:
        """Проверка связи с сервером Elasticsearch."""
        if not self.connection.ping():
            logging.error('Нет связи с сервером Elasticsearch')
            raise TransportError('Нет связи с сервером Elasticsearch')

    @backoff(logger=log_config.get_log)
    def push_index(self) -> None:
        """Отправка индекса в Elasticsearch."""
        body = schema.ES_SCHEMA
        self.check_connection()
        self.connection.indices.create(index=self.index_name, body=body)

    @backoff(logger=log_config.get_log)
    def push_bulk(self, bulk: list[models.ESDataConf], last_update_time: str) -> None:
        """
        Отправка пачки данных в Elasticsearch.

        Args:
            bulk: Список словарей для загрузки в Elasticserch.
            last_update_time: Время последнего обновления данных.
        """
        self.check_connection()
        self.connection.bulk(operations=bulk, index=self.index_name)
        logging.info('Данные успешно обновлены')
        self.state_maneger.set_state(key=Settings().state_key, value=last_update_time)
        logging.info(f'Дата последнего обновления данных: {last_update_time}')
