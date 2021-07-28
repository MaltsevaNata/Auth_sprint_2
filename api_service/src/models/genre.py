import uuid
from typing import Optional

from .custom_model import CustomModel


class Genre(CustomModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
