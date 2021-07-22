from core import db
from sqlalchemy.dialects.postgresql import UUID

from .base import ModelBase


class RefreshToken(ModelBase):
    __tablename__ = 'refresh_token'

    token = db.Column(db.String, nullable=False, unique=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Refresh token {self.token} for user {self.user_id} >'
