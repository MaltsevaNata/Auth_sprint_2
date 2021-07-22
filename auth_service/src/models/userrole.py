import uuid

from sqlalchemy.dialects.postgresql import UUID

from core import db


UserRole = db.Table("UserRole",
    db.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True),
    db.Column("userId", UUID(as_uuid=True), db.ForeignKey("user.id")),
    db.Column("roleId", UUID(as_uuid=True), db.ForeignKey("role.id")))