from datetime import timedelta
from typing import Any, Optional

import redis

from .config import Config


class RedisStorage:
    def __init__(self, host: str, port: int):
        self.conn = redis.Redis(host=host, port=port, db=0)

    def get(self, key: str) -> Any:
        """Retrieve the current value for a key"""
        return self.conn.get(key)

    def set(self, key: str, value, ttl: Optional[timedelta] = None):
        """Set a new value for a given key"""
        if ttl:
            self.conn.setex(key, ttl, value=value)
        else:
            self.conn.set(key, value=value)

    def mget(self, *keys: str) -> Any:
        """Retrieve values for a set of keys"""
        for key in keys:
            yield self.get(key)

    def mset(self, values: dict):
        """Set the value of several keys at once"""
        for key, value in values.items():
            self.set(key, value=value)

    def incr(self, key: str, amount: int = 1, default: int = 0) -> int:
        """Increment the value of a key by a given amount"""
        value = int(self.get(key) or default) + int(amount)
        self.set(key, value=value)
        return value

    def delete(self, key: str):
        self.conn.delete(key)


def get_redis(config_class=Config):
    return RedisStorage(host=config_class.REDIS_HOST,
                        port=config_class.REDIS_PORT)
