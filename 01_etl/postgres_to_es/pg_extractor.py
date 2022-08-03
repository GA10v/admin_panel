import datetime
import logging
from contextlib import contextmanager
from typing import Generator

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from components import log_config, models, sql_queries
from components.settings import Settings
from components.state import State
from components.utilities import backoff

log_config.get_log()


class PostgresExtractor:
    def __init__(
            self,
            dsl: models.DBConf,
            state_maneger: State,
            batch_size: int = 100,
            cursor_factory=DictCursor) -> None:
        """
        Args:
            dsl: Данные для подключения к psql.
            cursor_factory: Курсор.
            state_maneger: Объект класса State для хранения состояний.
            batch_size: Количество данных, передоваемых из psql.
        """
        self.dsl = dsl
        self.cursor_factory = cursor_factory
        self.state_maneger = state_maneger
        self.batch_size = batch_size

    @backoff(logger=log_config.get_log)
    def get_connection(self) -> _connection:
        """
        Реализация отказоустойчивости.

        Returns:
            _connection: Конектор.
        """
        return psycopg2.connect(**self.dsl, cursor_factory=self.cursor_factory)

    @contextmanager
    def get_pg_conn(self) -> _connection:
        """
        Контекстный менеджер для psql.

        Yields:
            _connection: Конектор.
        """
        conn = self.get_connection()
        yield conn
        conn.close()

    def get_last_update_time(self) -> datetime:
        """
        Получение времени последнего обновления данных.

        Returns:
            last_check: Дата последнего обновления данных.
        """
        try:
            last_check = self.state_maneger.get_state(Settings().state_key)
            return datetime.datetime.strptime(last_check[:-3], '%Y-%m-%d %H:%M:%S.%f')

        except (TypeError, ValueError):
            logging.warning('Отсутсвует файл с данными о последнем состоянии')
            last_check = '2021-01-01 00:0:00.000001'
            self.state_maneger.set_state(key=Settings().state_key, value=last_check)
            return datetime.datetime.strptime(last_check, '%Y-%m-%d %H:%M:%S.%f')

    def get_id(self) -> set:
        """
        Получение из PostgreSQL всех id для таблицы filmwork в которых были внесены изменения.

        Returns:
            result: Множество всех id для таблицы filmwork в которых были внесены изменения.
        """
        ids = []

        for query in sql_queries.get_query(self.get_last_update_time()):
            with self.get_pg_conn() as connection, connection.cursor() as cursor:
                cursor.execute(query)
                pg_data = cursor.fetchmany(self.batch_size)
                ids.append((str(item[0]) for item in pg_data))
        result = set(ids[0])
        return result

    @backoff(logger=log_config.get_log)
    def get_data(self) -> Generator[list[models.PGDataConf], None, None]:
        """
        Получение данных из PostgreSQL.

        Yields:
            Generator: Список словарей с данными из PostgreSQL.
        """
        try:
            ids = [id for id in self.get_id()]
            ids_count = ', '.join('%s' for _ in range(len(ids)))
            with self.get_pg_conn() as connection, connection.cursor() as cursor:
                cursor.execute(sql_queries.SQL_QUERY % ids_count, ids)
                desc = cursor.description
                column_names = [col[0] for col in desc]

                while pg_data := [dict(zip(column_names, row)) for row in cursor.fetchall()]:
                    yield pg_data
        except psycopg2.errors.SyntaxError:
            logging.info('Отсутствуют данные для обновления Elasticsearch')
