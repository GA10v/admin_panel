import uuid
from dataclasses import dataclass
from datetime import date, datetime
from typing import TypedDict


@dataclass
class FilmWorkSQL:
    """Определение типа данных для полей таблицы film_work."""

    title: str
    description: str
    creation_date: date
    type: str
    created_at: datetime
    updated_at: datetime
    file_path: str
    rating: float
    id: uuid.UUID


@dataclass
class PersonSQL:
    """Определение типа данных для полей таблицы person."""

    full_name: str
    created_at: datetime
    updated_at: datetime
    id: uuid.UUID


@dataclass
class GenreSQL:
    """Определение типа данных для полей таблицы genre."""

    name: str
    created_at: datetime
    updated_at: datetime
    description: str
    id: uuid.UUID


@dataclass
class GenreFilmWorkSQL:
    """Определение типа данных для полей таблицы genre_film_work."""

    id: uuid.UUID
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    created_at: datetime


@dataclass
class PersonFilmWorkSQL:
    """Определение типа данных для полей таблицы person_film_work."""

    id: uuid.UUID
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    role: str
    created_at: datetime


class SQLModelType(TypedDict):
    """TypedDict."""

    film_work: FilmWorkSQL
    person: PersonSQL
    genre: GenreSQL
    person_film_work: PersonFilmWorkSQL
    genre_film_work: GenreFilmWorkSQL
