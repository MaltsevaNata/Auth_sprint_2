from core import db

from .mixins import TimeStampedMixin, UUIDMixin


class ModelBase(db.Model, UUIDMixin):
    __abstract__ = True


class ModelTimeStamped(db.Model, UUIDMixin, TimeStampedMixin):
    __abstract__ = True
