from flask import current_app
from marshmallow import EXCLUDE, validates, ValidationError
from sqlalchemy.dialects.postgresql import UUID

from core import db, ma
from models.base import ModelTimeStamped

from core.decorators import catch_validation_errors


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


class GoogleUserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = GoogleUser
        unknown = EXCLUDE

    @validates("email")
    def validate_email(self, value):
        if current_app.google_user_manager.is_email_registered(value):
            raise ValidationError("Email is already registered.")


class GoogleUserManager:

    model = GoogleUser
    schema_class = GoogleUserSchema

    @catch_validation_errors
    def create_google_user(self, email, first_name, last_name, user_id):
        self.schema_class().load(dict(email=email, first_name=first_name, last_name=last_name, user_id=user_id))

        google_user = self.model(email=email, first_name=first_name, last_name=last_name, user_id=user_id)
        google_user.save()

        return google_user

    def get_by_email(self, value):
        return self.model.query.filter_by(email=value).first()

    def is_email_registered(self, value):
        return bool(self.get_by_email(value))
