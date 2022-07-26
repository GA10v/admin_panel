CREATE SCHEMA IF NOT EXISTS content;

ALTER ROLE app SET search_path TO "content";

CREATE TYPE film_type AS ENUM ('movie', 'tv_show');

CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    file_path TEXT DEFAULT NULL,
    creation_date DATE,
    rating FLOAT,
    type film_type NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE INDEX IF NOT EXISTS fw_title_idx ON 
content.film_work(title);

CREATE INDEX IF NOT EXISTS fw_creation_date_title_idx ON 
content.film_work(creation_date, title);

CREATE UNIQUE INDEX IF NOT EXISTS fw_rating_title_id_idx ON 
content.film_work(rating, title, id);

CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE INDEX IF NOT EXISTS p_full_name_idx ON 
content.person(full_name);

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid REFERENCES content.film_work (id) NOT NULL,
    person_id uuid REFERENCES content.person (id) NOT NULL,
    role TEXT NOT NULL,
    created timestamp with time zone
); 

CREATE UNIQUE INDEX IF NOT EXISTS person_film_work_fw_id_p_id_role_idx ON 
content.person_film_work(film_work_id, person_id, role);

CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created timestamp with time zone,
    modified timestamp with time zone
); 

CREATE INDEX IF NOT EXISTS genre_name_idx ON 
content.genre(name);

CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid REFERENCES content.film_work (id) NOT NULL,
    genre_id uuid REFERENCES content.genre (id) NOT NULL,
    created timestamp with time zone
); 

CREATE INDEX IF NOT EXISTS g_fw_genre_id_film_work_id_idx ON 
content.genre_film_work(genre_id, film_work_id);