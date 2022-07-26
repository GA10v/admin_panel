import os

from dotenv import load_dotenv

from . import models_pg, models_sql

load_dotenv()

DSL = {
    'host': os.environ.get('DB_HOST'),
    'database': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'port': os.environ.get('DB_PORT'),
}

DB_PATH = os.environ.get('SQLITE_PATH')

SQL_MODELS = {
    'film_work': models_sql.FilmWorkSQL,
    'genre': models_sql.GenreSQL,
    'genre_film_work': models_sql.GenreFilmWorkSQL,
    'person': models_sql.PersonSQL,
    'person_film_work': models_sql.PersonFilmWorkSQL,
}

PG_MODELS = {
    'film_work': models_pg.FilmWorkPG,
    'genre': models_pg.GenrePG,
    'genre_film_work': models_pg.GenreFilmWorkPG,
    'person': models_pg.PersonPG,
    'person_film_work': models_pg.PersonFilmWorkPG,
}
