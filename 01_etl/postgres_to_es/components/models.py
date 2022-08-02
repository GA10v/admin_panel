from typing import TypedDict
from uuid import UUID

from pydantic import BaseModel, validator
from pydantic.schema import List, Optional


class DBConf(TypedDict):
    """TypedDict."""

    host: str
    database: str
    user: str
    password: str
    port: str


class RedisConf(TypedDict):
    """TypedDict."""

    host: str
    port: int
    db: int


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


class ESDataConf(TypedDict):
    """TypedDict."""

    id: str
    title: str
    description: str
    imdb_rating: float
    type: str
    director: str
    actors_names: list[str] | list
    writers_names: list[str] | list
    actors: list[dict] | list
    writers: list[dict] | list
    genres: list[str]


class ESDocument(BaseModel):
    """Валидация данных для Elasticsearch."""

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
    @classmethod
    def valid_imdb_rating(cls, value) -> float:
        """Валидация поля imdb_rating.

        Args:
            value: Сырые данныме из PostgreSQL.

        Returns:
            value: Приведенные данныме к формату модели ESDocument.
        """
        if value is None:
            return 0.0
        return value

    @validator('description')
    @classmethod
    def valid_description(cls, value) -> str:
        """Валидация поля description.

        Args:
            value: Сырые данныме из PostgreSQL.

        Returns:
            value: Приведенные данныме к формату модели ESDocument.
        """
        if value is None:
            return ''
        return value

    @validator('director')
    @classmethod
    def valid_director(cls, value) -> str:
        """Валидация поля director.

        Args:
            value: Сырые данныме из PostgreSQL.

        Returns:
            value: Приведенные данныме к формату модели ESDocument.
        """
        if value is None:
            return ''
        return value

    @validator('actors_names')
    @classmethod
    def valid_actors_names(cls, value) -> list:
        """Валидация поля actors_names.

        Args:
            value: Сырые данныме из PostgreSQL.

        Returns:
            value: Приведенные данныме к формату модели ESDocument.
        """
        if value is None:
            return []
        return value

    @validator('writers_names')
    @classmethod
    def valid_writers_names(cls, value) -> list:
        """Валидация поля writers_names.

        Args:
            value: Сырые данныме из PostgreSQL.

        Returns:
            value: Приведенные данныме к формату модели ESDocument.
        """
        if value is None:
            return []
        return value
