import os

from dotenv import load_dotenv

from . import models_pg

load_dotenv()

DSL_PG = {
    'host': os.environ.get('DB_HOST'),
    'database': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'port': os.environ.get('DB_PORT'),
}


SQL_QUERY = """
    SELECT
    fw.id,
    fw.title,
    fw.description,
    fw.rating,
    fw.type,
    fw.created,
    fw.modified,
    COALESCE (
        json_agg(
            DISTINCT jsonb_build_object(
                'person_role', pfw.role,
                'person_id', p.id,
                'person_name', p.full_name
            )
        ) FILTER (WHERE p.id is not null),
        '[]'
    ) as persons,
    array_agg(DISTINCT g.name) as genres
    FROM content.film_work fw
    LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
    LEFT JOIN content.person p ON p.id = pfw.person_id
    LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
    LEFT JOIN content.genre g ON g.id = gfw.genre_id
    WHERE fw.modified > '%s'
    GROUP BY fw.id
    ORDER BY fw.modified
    LIMIT 100; 
"""

PG_MODELS = {
    'film_work': models_pg.FilmWorkPG,
    'genre': models_pg.GenrePG,
    'genre_film_work': models_pg.GenreFilmWorkPG,
    'person': models_pg.PersonPG,
    'person_film_work': models_pg.PersonFilmWorkPG,
}
