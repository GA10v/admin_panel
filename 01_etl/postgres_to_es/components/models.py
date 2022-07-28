from typing import TypedDict
from uuid import UUID
from pydantic import BaseModel, validator
from pydantic.schema import Optional, List


class DBConf(TypedDict):
    """TypedDict."""

    host: str
    database: str
    user: str
    password: str
    port: str


class PGDataConf(TypedDict):
    """TypedDict."""

    id: UUID
    title: str
    description: str | None
    imdb_rating: float | None
    type: str
    modified: str
    director: str | None
    actors_names: list[str] | None
    writers_names: list[str] | None
    actors: list[dict]
    writers: list[dict]
    genres: list[str]


class ESDocument(BaseModel):
    id: UUID
    imdb_rating: Optional[float]
    genre: Optional[List]
    title: str
    description: Optional[str]
    director: Optional[str]
    actors_names: Optional[List]
    writers_names: Optional[List]
    actors: List
    writers: List

    @validator('imdb_rating')
    def valid_imdb_rating(cls, value):
        if value is None:
            return 0.0
        return value

    @validator('description')
    def valid_description(cls, value):
        if value is None:
            return ''
        return value

    @validator('director')
    def valid_director(cls, value):
        if value is None:
            return ''
        return value

    @validator('actors_names')
    def valid_actors_names(cls, value):
        if value is None:
            return []
        return value

    @validator('writers_names')
    def valid_writers_names(cls, value):
        if value is None:
            return []
        return value
