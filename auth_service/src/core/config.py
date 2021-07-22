import os

from datetime import timedelta
from pathlib import Path
from typing import List


basedir = Path(__file__).parent.parent


class Config(object):
    # App
    SECRET_KEY: str = os.environ["SECRET_KEY"]

    # Database
    SQLALCHEMY_DATABASE_URI: str = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost:5432/auth")

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # JWT
    JWT_REFRESH_TOKEN_EXPIRES: int = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 365 * 24 * 60 * 60))
    JWT_ACCESS_TOKEN_EXPIRES: int = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 15 * 60))

    # Redis
    REDIS_HOST: str = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT: int = os.environ.get('REDIS_PORT', 6379)
    REDIS_TTL: timedelta = timedelta(minutes=16)
    REDIS_EXTENDED_TTL: timedelta = timedelta(days=366)

    # Mail
    MAIL_SERVER: str = os.environ.get("MAIL_SERVER", "localhost")
    MAIL_PORT: int = os.environ.get("MAIL_PORT", 25)
    MAIL_USE_TLS: bool = os.environ.get("MAIL_USE_TLS")
    MAIL_USERNAME: str = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD: str = os.environ.get("MAIL_PASSWORD")
    ADMINS: List[str] = ["admin@example.org"]