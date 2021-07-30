import datetime

from user_agents import parse

from core import db
from sqlalchemy.dialects.postgresql import UUID

from .base import ModelBase


def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]


class LoginHistory(ModelBase):
    __tablename__ = 'login_history_master'
    __table_args__ = {
        'postgresql_partition_by': 'LIST (user_device_type)'
    }

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    user_agent = db.Column(db.String, nullable=False)
    ip_addr = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    user_device_type = db.Column(db.Text, nullable=False, primary_key=True, unique=True)

    def __repr__(self):
        return f'<User {self.user_id} logged in {self.timestamp}>'


    @property
    def user_device(self):
        return self.user_device_type

    @user_device.setter
    def user_device(self, ua_string):
        user_agent = parse(ua_string)
        if user_agent.is_mobile:
            self.user_device_type = 'mobile'
        elif not user_agent.is_pc and \
                'smart' in str(user_agent.device.model).lower() or 'smart-tv' in ua_string.lower():
            self.user_device_type = 'smart'
        else:
            self.user_device_type = 'web'

    def to_dict(self):
        return {
            'user_agent': self.user_agent,
            'timestamp': dump_datetime(self.timestamp),
            'ip_addr': self.ip_addr,
            'user_device': self.user_device
        }
