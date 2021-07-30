import uuid

from pydantic import Field

from .custom_model import CustomModel


class Person(CustomModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    role: list[str] = Field(default_factory=list)
    film_ids: list[uuid.UUID]
