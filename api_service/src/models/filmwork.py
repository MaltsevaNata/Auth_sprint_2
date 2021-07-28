import uuid
from typing import Optional

from pydantic import Field

from .custom_model import CustomModel
from .genre import Genre


class FilmWork(CustomModel):
    # TODO: по ТЗ нужны еще поля: дата создания, возрастной ценз, имя файла
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    imdb_rating: Optional[float] = None
    genres: list[Genre] = Field(default_factory=list)
    actors: list[str] = Field(default_factory=list)
    directors: list[str] = Field(default_factory=list)
    writers: list[str] = Field(default_factory=list)
