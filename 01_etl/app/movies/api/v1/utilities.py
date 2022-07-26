from typing import TypedDict


class MovieContextType(TypedDict):
    """TypedDict."""

    id: str
    title: str
    description: str
    creation_date: str
    rating: float
    type: str
    genres: list[str]
    actors: list[str]
    directors: list[str]
    writers: list[str]


class MoviesContextType(TypedDict):
    """TypedDict."""

    count: int
    total_pages: int
    prev: None | int
    next: None | int
    results: list[MovieContextType]
