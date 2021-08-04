import random
import string

from core import db, ma, Config
from core.decorators import catch_validation_errors
from flask import current_app
from marshmallow import EXCLUDE, ValidationError, validates
from werkzeug.security import check_password_hash, generate_password_hash

from .base import ModelTimeStamped
from .role import Role
from .userrole import UserRole


class User(ModelTimeStamped):
    __tablename__ = "user"

    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    roles = db.relationship("Role", secondary=UserRole, back_populates="users")
    is_active_2fa = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    totp_secret = db.Column(db.String, nullable=True)
    google_email = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f"<User {self.username} {self.roles}>"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.roles is None:
            self.roles = Role.query.filter_by(default=True).first()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def as_dict(self):
        columns = dict(self.__table__.columns)
        excluded = ("password_hash", "is_verified", "totp_secret")
        return {c: getattr(self, c) for c in columns if c not in excluded}

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_roles(self):
        roles = [role.name for role in self.roles]
        return roles

    def activate_2fa(self):
        self.is_active_2fa = True
        self.save()

    def deactivate_2fa(self):
        self.is_active_2fa = False
        self.save()

    def save(self):
        """Save the current instance."""
        db.session.add(self)
        db.session.commit()


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ("password_hash",)
        unknown = EXCLUDE

    @validates("username")
    def validate_username(self, value):
        if current_app.user_manager.is_username_registered(value):
            raise ValidationError("Username already exists.")

    @validates("email")
    def validate_email(self, value):
        if current_app.user_manager.is_email_registered(value):
            raise ValidationError("Email is already registered.")


class UserManager:

    model = User
    schema_class = UserSchema

    @catch_validation_errors
    def create_user(self, username, password, email):

        self.schema_class().load(dict(username=username, email=email))

        user = self.model(username=username, email=email)
        user.set_password(password)
        user.save()

        return user

    def create_google_user(self, google_email, first_name, last_name):

        self.schema_class().load(dict(
            username=google_email,
            email=google_email,
            google_email=google_email,
            first_name=first_name,
            last_name=last_name
        ))

        user = self.model(
            username=google_email,
            email=google_email,
            google_email=google_email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(self.generate_password(size=Config.MOCK_PASSWORD_LENGTH))

        user.save()
        return user

    @catch_validation_errors
    def update_user(self, user, data):
        # TODO: Fix this
        # validated_data = self.schema_class().load(data)

        for key, value in data.items():
            setattr(user, key, value)

        user.save()
        return user

    def add_role(self, user, new_role):
        role = Role.query.filter_by(name=new_role).first_or_404()
        user.roles.append(role)
        db.session.commit()

    def remove_role(self, user, removed_role):
        role = Role.query.filter_by(name=removed_role).first_or_404()
        user.roles.remove(role)
        db.session.commit()

    def is_username_registered(self, value):
        return bool(self.get_by_username(value))

    def is_email_registered(self, value):
        return bool(self.get_by_email(value))

    def get_by_username(self, value):
        return self.model.query.filter_by(username=value).first()

    def get_by_email(self, value):
        return self.model.query.filter_by(email=value).first()

    def get_by_id(self, value):
        return self.model.query.filter_by(id=value).first()

    def get_by_google_email(self, value):
        return self.model.query.filter_by(google_email=value).first()

    def generate_password(self, size, chars=string.ascii_letters + string.punctuation + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
