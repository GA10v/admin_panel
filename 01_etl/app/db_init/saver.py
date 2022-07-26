import logging
from dataclasses import fields

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import execute_batch

from components import constants, log_config, models_pg

log_config.get_log()


class PSQLSaver:
    def __init__(self, connection: _connection, page_size=1000):
        self.connection = connection
        self.page_size = page_size

    def save_all_data(self, data: list[models_pg.PGModelType]) -> None:
        """Метод сохранения всех данных в базу.

        Args:
            data: Список кортежей с данными для загрузки в pg
        """
        for table_name, table_data in data:
            self.save_data(table_name, table_data)

    def save_data(self, table_name: str, data: list[models_pg.PGModelType]) -> None:
        """Метод сохранения данных в таблицу.

        Args:
            table_name: Имя таблицы
            data: Список кортежей с данными для загрузки в pg
        """
        fields_list = [field.name for field in fields(constants.PG_MODELS.get(table_name))]
        fields_string = ', '.join(fields_list)
        values_string = ', '.join('%s' for _ in range(len(fields_list)))
        query = f'INSERT INTO content.{table_name} ({fields_string}) \
                 VALUES ({values_string}) ON CONFLICT DO NOTHING; '
        data = [tuple(getattr(row, field) for field in fields_list) for row in data]

        with self.connection as con:
            with con.cursor() as curs:
                try:
                    execute_batch(curs, query, data, page_size=self.page_size)
                except psycopg2.Error as er:
                    logging.error(er)
