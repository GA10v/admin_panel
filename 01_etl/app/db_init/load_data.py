import sqlite3

from psycopg2.extensions import connection as _connection

from components import constants, utilities
from loader import SQLiteLoader
from saver import PSQLSaver


def load_from_sqlite(sqlite_conn: sqlite3.Connection, pg_conn: _connection) -> None:
    """Основной метод загрузки данных из SQLite в Postgres.

    Args:
        sqlite_conn: Контекстный менеджер для sqlite
        pg_conn: Контекстный менеджер для psql
    """
    sql_loader = SQLiteLoader(connection=sqlite_conn)
    psql_saver = PSQLSaver(pg_conn)

    data = sql_loader.load_data()
    psql_saver.save_all_data(data)


if __name__ == '__main__':
    if utilities.check_pg_models(constants.DSL):
        with utilities.sqlite_conn_context(constants.DB_PATH) as sqlite_conn, utilities.pg_conn_context(constants.DSL) as pg_conn:
            load_from_sqlite(sqlite_conn, pg_conn)
