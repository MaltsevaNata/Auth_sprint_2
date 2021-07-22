from datetime import timedelta
from typing import Any

import redis

from .config import Config


class RedisStorage:
    def __init__(self, host: str, port: int):
        self.conn = redis.Redis(host=host, port=port, db=0)

    def get(self, key: str) -> Any:
        return self.conn.get(key)

    def set(self, key: str, ttl: timedelta, value):
        self.conn.setex(key, ttl, value=value)

    def delete(self, key: str):
        self.conn.delete(key)


def get_redis(config_class=Config):
    return RedisStorage(host=config_class.REDIS_HOST,
                        port=config_class.REDIS_PORT)
