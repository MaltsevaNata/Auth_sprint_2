from typing import Set
from dataclasses import dataclass, field


@dataclass
class MovieFromSqlite:
    title: str
    imdb_rating: float
    genres: Set[str]
    id: str
    writers: Set[str]
    actors: Set[str]
    directors: Set[str]
    filmwork_type: str = field(default='movie')
    description: str = field(default='')
