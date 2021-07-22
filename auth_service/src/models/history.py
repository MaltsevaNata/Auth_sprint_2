import datetime

from core import db
from sqlalchemy.dialects.postgresql import UUID

from .base import ModelBase


def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]


class LoginHistory(ModelBase):
    __tablename__ = 'login_history'
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    user_agent = db.Column(db.String, nullable=False)
    ip_addr = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<User {self.user_id} logged in {self.timestamp}>'

    def to_dict(self):
        return {
            'user_agent': self.user_agent,
            'timestamp': dump_datetime(self.timestamp),
            'ip_addr': self.ip_addr
        }
