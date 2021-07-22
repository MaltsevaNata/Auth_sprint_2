import os
import time

import redis


def check_connection(host: str, port: int):
    conn = redis.Redis(host=host, port=port, db=0)
    val = conn.ping()
    if val == 'PONG':
        return True
    return False


def main():
    host = os.environ.get('REDIS_HOST', 'localhost')
    port = os.environ.get('REDIS_PORT', 6379)
    while True:
        try:
            check_connection(host, port)
        except (OSError, redis.RedisError):
            time.sleep(3)
        else:
            exit()


if __name__ == '__main__':
    main()
