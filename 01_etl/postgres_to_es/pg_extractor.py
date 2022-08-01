import datetime
from psycopg2.extensions import connection as _connection
from components import log_config, constants, utilities, sql_queries, models, state
import logging
from typing import Generator
import json
from components.state import State

log_config.get_log()


class PostgresExtractor:
    def __init__(self, connection: _connection, state_maneger: State, batch_size: int = 100) -> None:
        self.connection = connection
        self.state_maneger = state_maneger
        self.batch_size = batch_size

    def get_last_update_time(self) -> datetime:
        """Получение времени последнего обновления данных."""
        try:
            last_check = self.state_maneger.get_state(constants.STATE_KEY)
            return datetime.datetime.strptime(last_check[:-3], '%Y-%m-%d %H:%M:%S.%f')

        except (TypeError, ValueError):
            logging.warning('Отсутсвует файл с данными о последнем состоянии')
            last_check = '2021-01-01 00:0:00.000001'
            self.state_maneger.set_state(key=constants.STATE_KEY, value=last_check)
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
                with self.connection.cursor() as cursor:
                    cursor.execute(query)
                    pg_data = cursor.fetchall()
                    ids.append((str(x[0]) for x in pg_data))
            result = set(ids[0])
            return result
        except Exception as er:
            logging.error(er)
            raise er

    def get_data(self) -> Generator[list[models.PGDataConf], None, None]:
        """
        Получение данных из PostgreSQL.

        Yields:
            Generator: Список словарей с данными из PostgreSQL
        """
        try:
            ids = [id for id in self.get_id()]
            ids_count = ', '.join('%s' for _ in range(len(ids)))
            with self.connection.cursor() as cursor:
                cursor.execute(sql_queries.SQL_QUERY % ids_count, ids)

                desc = cursor.description
                column_names = [col[0] for col in desc]

                while pg_data := [dict(zip(column_names, row)) for row in cursor.fetchmany(self.batch_size)]:
                    yield pg_data
        except Exception as er:
            logging.error(er)
            raise er


if __name__ == '__main__':
    storage = state.JsonFileStorage(constants.STATE_FILE)
    state_maneger = state.State(storage)
    with utilities.pg_conn_context(constants.DSL_PG) as pg_conn:
        pg_loader = PostgresExtractor(connection=pg_conn, state_maneger=state_maneger, batch_size=100)
        data = [x for x in pg_loader.get_data()][0]
        print(len(data))
        with open('1.json', 'w') as f:
            json.dump(data, f, indent=4)
