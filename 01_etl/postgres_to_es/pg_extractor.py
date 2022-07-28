import datetime
from psycopg2.extensions import connection as _connection
from components import log_config, constants, utilities
import logging
from typing import Generator

log_config.get_log()


class PostgresExtractor:
    def __init__(self, connection: _connection, batch_size: int) -> None:
        self.connection = connection
        self.batch_size = batch_size

    def get_data(self, last_update_time: datetime, query: str) -> Generator[list, None, None]:
        """
        Получение данных из PostgreSQL.

        Args:
            last_update_time: Время последнего обновления данных
            query: Запрос к PostgreSQL

        Yields:
            Generator: Список словарей с данными из PostgreSQL
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(constants.SQL_QUERY % last_update_time)

                desc = cursor.description
                column_names = [col[0] for col in desc]

                while pg_data := [dict(zip(column_names, row)) for row in cursor.fetchmany(self.batch_size)]:
                    yield pg_data
        except Exception as er:
            logging.error(er)


if __name__ == '__main__':
    with utilities.pg_conn_context(constants.DSL_PG) as pg_conn:
        pg_loader = PostgresExtractor(connection=pg_conn, batch_size=1)
        data = pg_loader.get_data(last_update_time=datetime.datetime.now())
        print([x[0] for x in data])
