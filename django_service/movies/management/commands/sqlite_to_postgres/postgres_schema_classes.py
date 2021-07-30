from datetime import datetime, timezone
import uuid
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Filmwork:
    title: str
    created: datetime = datetime.now(timezone.utc)
    modified: datetime = datetime.now(timezone.utc)
    description: str = field(default='')
    rating: float = field(default=0.0)
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    filmwork_type: str = field(default='movie')
    age_limit: Optional[int] = field(default=None)
    creation_date: Optional[datetime] = field(default=None)

@dataclass
class Genre:
    name: str
    created: datetime = datetime.now(timezone.utc)
    modified: datetime = datetime.now(timezone.utc)
    description: str = field(default='')
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Person:
    first_name: str
    last_name: str
    created: datetime = datetime.now(timezone.utc)
    modified: datetime = datetime.now(timezone.utc)
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class PersonRole:
    role: str
    filmwork_id: uuid.UUID
    person_id: uuid.UUID
    created: datetime = datetime.now(timezone.utc)
    modified: datetime = datetime.now(timezone.utc)
    id: uuid.UUID = field(default_factory=uuid.uuid4)

@dataclass
class FilmworkGenres:
    filmwork_id: uuid.UUID
    genre_id: uuid.UUID


@dataclass
class FilmworkPersons:
    filmwork_id: uuid.UUID
    person_id: uuid.UUID
