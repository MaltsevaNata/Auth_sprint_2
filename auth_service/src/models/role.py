from core import db

from .base import ModelTimeStamped
from .userrole import UserRole


class Permissions:
    USER = 1
    SUBSCRIBER = 2
    ADMIN = 4


class Role(ModelTimeStamped):
    __tablename__ = "role"

    name = db.Column(db.String, unique=True, nullable=False)
    permissions = db.Column(db.Integer)
    default = db.Column(db.Boolean, default=False)
    users = db.relationship("User", secondary=UserRole, back_populates="roles")

    def __repr__(self):
        return f"<Role {self.name}>"

    def __str__(self):
        return str(self.name)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permission(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def as_dict(self):
        columns = dict(self.__table__.columns)
        return {c: getattr(self, c) for c in columns}
