from . import constants
from typing import Generator
import datetime


def get_query(last_update_time: datetime) -> Generator[str, None, None]:
    for table in constants.PG_MODELS:
        query = f"""SELECT
                    content.film_work.id
                    FROM content.film_work 
                    LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = content.film_work.id
                    LEFT JOIN content.person ON content.person.id = pfw.person_id
                    LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = content.film_work.id
                    LEFT JOIN content.genre ON content.genre.id = gfw.genre_id
                    WHERE content.{table}.modified > '{last_update_time}'
                    GROUP BY content.film_work.id;"""
        yield query


SQL_QUERY = """
    SELECT
    fw.id,
    fw.title,
    fw.description,
    fw.rating AS imdb_rating,
    fw.type,
    to_char(fw.modified, 'YYYY-MM-DD HH24:MI:SS.FF6TZH') AS modified,
    COALESCE (
            string_agg(DISTINCT p.full_name, '')
            FILTER(WHERE p.id is not null AND pfw.role = 'director'),
            ''
            ) AS director,
    array_agg(DISTINCT p.full_name) FILTER(WHERE p.id is not null AND pfw.role = 'actor') AS actors_names,
    array_agg(DISTINCT p.full_name) FILTER(WHERE p.id is not null AND pfw.role = 'writer') AS writers_names,
    COALESCE (
            json_agg(
                DISTINCT jsonb_build_object(
                    'id', p.id,
                    'name', p.full_name
                )
            ) FILTER (WHERE p.id is not null AND pfw.role = 'actor'),
            '[]'
        ) as actors,
    COALESCE (
            json_agg(
                DISTINCT jsonb_build_object(
                    'id', p.id,
                    'name', p.full_name
                )
            ) FILTER (WHERE p.id is not null AND pfw.role = 'writer'),
            '[]'
        ) as writers,
    array_agg(DISTINCT g.name) as genres
    FROM content.film_work fw
    LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
    LEFT JOIN content.person p ON p.id = pfw.person_id
    LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
    LEFT JOIN content.genre g ON g.id = gfw.genre_id
    WHERE fw.id IN (%s)
    GROUP BY fw.id
    ORDER BY modified
"""
