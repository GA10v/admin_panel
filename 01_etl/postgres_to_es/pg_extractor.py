import datetime
from psycopg2.extensions import connection as _connection
from components import log_config, constants, sql_queries, models, state
from components.utilities import backoff
import logging
from typing import Generator
import json
from components.state import State

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from contextlib import contextmanager

log_config.get_log()


class PostgresExtractor:
    def __init__(self, dsl: models.DBConf, state_maneger: State, batch_size: int = 100, cursor_factory=DictCursor) -> None:
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

    @backoff()
    def get_connection(self) -> _connection:
        """ Реализация отказоустойчивости.

        Returns:
            _connection: Конектор.      
        """
        return psycopg2.connect(**self.dsl, cursor_factory=self.cursor_factory)

    @contextmanager
    def get_pg_conn(self) -> _connection:
        """Контекстный менеджер для psql.

        Yields:
            _connection: Конектор
        """
        try:
            conn = self.get_connection()
            yield conn
        # except psycopg2.Error as er:
        #     logging.error(er)
        #     raise er
        finally:
            conn.close()

    def get_last_update_time(self) -> datetime:
        """Получение времени последнего обновления данных."""
        try:
            last_check = self.state_maneger.get_state(constants.STATE_KEY)
            return datetime.datetime.strptime(last_check[:-3], '%Y-%m-%d %H:%M:%S.%f')

        except (TypeError, ValueError):
            logging.warning('Отсутсвует файл с данными о последнем состоянии')
            last_check = '2021-01-01 00:0:00.000001'
            self.state_maneger.set_state(
                key=constants.STATE_KEY, value=last_check)
            return datetime.datetime.strptime(last_check, '%Y-%m-%d %H:%M:%S.%f')

    def get_id(self) -> set:
        """
        Получение из PostgreSQL всех id для таблицы filmwork в которых были внесены изменения.

        Returns:
            result: Множество всех id для таблицы filmwork в которых были внесены изменения.
        """
        ids = []
        try:
            for query in sql_queries.get_query(self.get_last_update_time()):
                with self.get_pg_conn() as connection, connection.cursor() as cursor:
                    cursor.execute(query)
                    pg_data = cursor.fetchall()
                    ids.append((str(x[0]) for x in pg_data))
            result = set(ids[0])
            return result
        except Exception as er:
            logging.error(er)

    def get_data(self) -> Generator[list[models.PGDataConf], None, None]:
        """
        Получение данных из PostgreSQL.

        Yields:
            Generator: Список словарей с данными из PostgreSQL
        """
        try:
            ids = [id for id in self.get_id()]
            ids_count = ', '.join('%s' for _ in range(len(ids)))
            with self.get_pg_conn() as connection, connection.cursor() as cursor:
                cursor.execute(sql_queries.SQL_QUERY % ids_count, ids)
                desc = cursor.description
                column_names = [col[0] for col in desc]

                while pg_data := [dict(zip(column_names, row)) for row in cursor.fetchmany(self.batch_size)]:
                    yield pg_data
        except Exception as er:
            logging.error(er)


if __name__ == '__main__':
    storage = state.JsonFileStorage(constants.STATE_FILE)
    state_maneger = state.State(storage)
    extractor = PostgresExtractor(dsl=constants.DSL_PG, state_maneger=state_maneger, batch_size=10000)
    data = [x for x in extractor.get_data()][0]
    print(len(data))
    with open('1.json', 'w') as f:
        json.dump(data, f, indent=4)
