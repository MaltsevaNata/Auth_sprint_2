import os
import time

import psycopg2


def main():
    dsl = {'dbname': os.environ.get('POSTGRES_DB', 'auth_sprint'),
           'user': os.environ.get('POSTGRES_USER', 'user'),
           'password': os.environ.get('POSTGRES_PASSWORD'),
           'host': os.environ.get('POSTGRES_HOST', 'localhost'),
           'port': os.environ.get('POSTGRES_PORT', 5432),
           }
    while True:
        try:
            psycopg2.connect(**dsl)
        except (OSError, psycopg2.OperationalError):
            time.sleep(3)
        else:
            exit()


if __name__ == '__main__':
    main()
