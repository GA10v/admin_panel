import datetime
from psycopg2.extensions import connection as _connection
from components import log_config, constants, utilities, sql_queries
import logging
from typing import Generator
import json

log_config.get_log()


class PostgresExtractor:
    def __init__(self, connection: _connection, batch_size: int) -> None:
        self.connection = connection
        self.batch_size = batch_size

    def get_id(self, last_update_time: datetime) -> set:
        """
        Получение из PostgreSQL всех id для таблицы filmwork в которых были внесены изменения.

        Args:
            last_update_time: Время последнего обновления данных.

        Returns:
            result: Множество всех id для таблицы filmwork в которых были внесены изменения.
        """
        
        ids = []
        try:
            for query in sql_queries.get_query(last_update_time):
                with self.connection.cursor() as cursor:
                    cursor.execute(query)
                    pg_data=cursor.fetchall()
                    ids.append((str(x[0]) for x in pg_data))
            result = set(ids[0])
            return result
        except Exception as er:
            logging.error(er)

    def get_data(self, last_update_time: datetime) -> Generator[list, None, None]:
        """
        Получение данных из PostgreSQL.

        Args:
            last_update_time: Время последнего обновления данных

        Yields:
            Generator: Список словарей с данными из PostgreSQL
        """
        try:
            ids = [id for id in self.get_id(last_update_time)]
            ids_count = ', '.join('%s' for _ in range(len(ids)))
            with self.connection.cursor() as cursor:
                cursor.execute(sql_queries.SQL_QUERY % ids_count, ids)

                desc = cursor.description
                column_names = [col[0] for col in desc]

                while pg_data := [dict(zip(column_names, row)) for row in cursor.fetchmany(self.batch_size)]:
                    yield pg_data
        except Exception as er:
            logging.error(er)


if __name__ == '__main__':
    with utilities.pg_conn_context(constants.DSL_PG) as pg_conn:
        pg_loader=PostgresExtractor(connection = pg_conn, batch_size = 100)
        data=pg_loader.get_data(last_update_time = datetime.datetime.now())
        with open('2.json', 'w') as f:
            json.dump([x for x in data][0], f, indent=4)
