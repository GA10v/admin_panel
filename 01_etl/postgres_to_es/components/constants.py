import os

from dotenv import load_dotenv


load_dotenv()

PG_MODELS = ['filmwork', 'person', 'genre']

DSL_PG = {
    'host': os.environ.get('DB_HOST'),
    'database': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'port': os.environ.get('DB_PORT'),
}

SQL_QUERY_FW = """
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
    WHERE fw.modified < '%s'
    GROUP BY fw.id
    ORDER BY modified
    LIMIT 100;
"""

SQL_QUERY_P = """
        SELECT
    fw.id,
    fw.title,
    fw.description,
    fw.rating AS imdb_rating,
    fw.type,
    to_char(p.modified, 'YYYY-MM-DD HH24:MI:SS.FF6TZH') AS modified,
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
    WHERE p.modified < '%s'
    GROUP BY fw.id
    ORDER BY modified
    LIMIT 100;
"""

SQL_QUERY_G = """
        SELECT
    fw.id,
    fw.title,
    fw.description,
    fw.rating AS imdb_rating,
    fw.type,
    to_char(g.modified, 'YYYY-MM-DD HH24:MI:SS.FF6TZH') AS modified,
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
    WHERE g.modified < '%s'
    GROUP BY fw.id
    ORDER BY modified
    LIMIT 100;
"""

SQL_QUERIES = {
    'filmwork': SQL_QUERY_FW,
    'person': SQL_QUERY_P,
    'genre': SQL_QUERY_G,
}
