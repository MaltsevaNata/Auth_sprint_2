import datetime
import uuid

from core import db
from sqlalchemy.dialects.postgresql import UUID


class UUIDMixin:
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)


class TimeStampedMixin:
    __abstract__ = True

    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
