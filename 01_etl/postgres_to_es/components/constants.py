import os

from dotenv import load_dotenv

from . import models_pg

load_dotenv()

# добавить pg
DSL = {
    'host': os.environ.get('DB_HOST'),
    'database': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'port': os.environ.get('DB_PORT'),
}


PG_MODELS = {
    'film_work': models_pg.FilmWorkPG,
    'genre': models_pg.GenrePG,
    'genre_film_work': models_pg.GenreFilmWorkPG,
    'person': models_pg.PersonPG,
    'person_film_work': models_pg.PersonFilmWorkPG,
}
