import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import TypedDict


@dataclass
class FilmWorkPG:
    """Определение типа данных для полей таблицы film_work."""

    title: str
    description: str
    creation_date: date
    type: str
    created: datetime
    modified: datetime
    file_path: str
    rating: float = field(default=0.0)
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class PersonPG:
    """Определение типа данных для полей таблицы person."""

    full_name: str
    created: datetime
    modified: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class GenrePG:
    """Определение типа данных для полей таблицы genre."""

    name: str
    created: datetime
    modified: datetime
    description: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class GenreFilmWorkPG:
    """Определение типа данных для полей таблицы genre_film_work."""

    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    created: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class PersonFilmWorkPG:
    """Определение типа данных для полей таблицы person_film_work."""

    film_work_id: uuid.UUID
    person_id: uuid.UUID
    role: str
    created: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)


class DBConf(TypedDict):
    """TypedDict."""

    host: str
    database: str
    user: str
    password: str
    port: str


class PGModelType(TypedDict):
    """TypedDict."""

    film_work: FilmWorkPG
    person: PersonPG
    genre: GenrePG
    person_film_work: PersonFilmWorkPG
    genre_film_work: GenreFilmWorkPG
