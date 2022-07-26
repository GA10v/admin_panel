import logging
import sqlite3
from dataclasses import asdict
from typing import Generator

from components import constants, log_config, models_pg, models_sql

log_config.get_log()


class SQLiteLoader:
    def __init__(self, connection: sqlite3.Connection, batch_size=1000):
        self.connection = connection
        self.batch_size = batch_size

    def load_data(self) -> Generator[str, list[models_pg.PGModelType], None]:
        """Метод передачи всех данных из sqlite.

        Yields:
            table_name: Название таблиы
            data: Список кортежей с данными из таблицы sqlite
        """
        for table_name in self.get_tables():
            sql_model = constants.SQL_MODELS.get(table_name)
            pg_model = constants.PG_MODELS.get(table_name)
            if not sql_model:
                continue
            for data in self.get_data(table_name, sql_model, pg_model):
                yield table_name, data

    def get_tables(self) -> list[str]:
        """Метод получения списка таблиц sqlite.

        Returns:
            list: Список имен таблиц из sqlite
        """
        curs = self.connection.cursor()
        curs.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY length(name);')
        return [data[0] for data in curs.fetchall()]

    @staticmethod
    def transform_sql_data(pg_model: models_pg.PGModelType, data: list[models_sql.SQLModelType]) -> list[models_pg.PGModelType]:
        """Метод приведения данных из sql_models в pg_models.

        Args:
            tpg_model: ДК
            data: Список данных в формате sql_models

        Returns:
            list: Список данных приведенных к формату pg_models
        """
        model = pg_model
        rows = []
        for row in data:
            _dict = asdict(row)
            try:
                _dict['created'] = _dict.pop('created_at')
            except KeyError:
                rows.append(_dict)
                continue
            try:
                _dict['modified'] = _dict.pop('updated_at')
            except KeyError:
                rows.append(_dict)
                continue
            rows.append(_dict)
        return [model(**data) for data in rows]

    def get_data(self, table_name: str, sql_model: models_sql.SQLModelType, pg_model: models_pg.PGModelType) -> Generator[list[models_pg.PGModelType], None, None]:
        """Метод получения данных из таблицы sqlite.

        Args:
            table_name: Имя таблицы
            sql_model: ДК sql
            pg_model: ДК pg

        Yields:
            list: список кортежей с данными из таблицы sqlite
        """
        try:
            curs = self.connection.cursor()
            curs.execute(f'SELECT * FROM {table_name};')
            columns = [column[0] for column in curs.description]
        except sqlite3.Error as er:
            logging.error(er)
        while rows := curs.fetchmany(size=self.batch_size):
            try:
                sql_data = [sql_model(**dict(zip(columns, data))) for data in rows]
            except Exception as er:
                logging.error(er)
            pg_data = self.transform_sql_data(pg_model, sql_data)
            yield pg_data
