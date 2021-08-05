from sqlalchemy.dialects.postgresql import UUID

from core import db
from models.base import ModelTimeStamped


class GoogleUser(ModelTimeStamped):
    __tablename__ = "google_user"

    email = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), unique=True, nullable=False)

    def __repr__(self):
        return f"<Google User {self.email}>"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def save(self):
        """Save the current instance."""
        db.session.add(self)
        db.session.commit()
