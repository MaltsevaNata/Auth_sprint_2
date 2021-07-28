import os
import sqlite3
import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from .sqlite_to_postgres.PostgresSaver import PostgresSaver
from .sqlite_to_postgres.SQLiteLoader import SQLiteLoader

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Loads data from file db.sqlite to postgres'

    def handle(self, *args, **kwargs):
        dsl = {'dbname': os.environ.get('SQL_DATABASE', 'movies'), 'user': os.environ.get('SQL_USER', 'postgres'),
               'password': os.environ.get('SQL_PASSWORD', 'password') , 'host': os.environ.get('SQL_HOST', 'movies_postgres'),
               'port': os.environ.get('SQL_PORT', 5432)}
        path = os.path.realpath('./movies/management/commands/sqlite_to_postgres/db.sqlite')
        with sqlite3.connect(path) as sqlite_conn, psycopg2.connect(
                **dsl, cursor_factory=DictCursor) as pg_conn:
            self.load_from_sqlite(sqlite_conn, pg_conn)
        print('Loaded successfully')

    def load_from_sqlite(self, connection: sqlite3.Connection, pg_conn: _connection):
        """Основной метод загрузки данных из SQLite в Postgres"""
        postgres_saver = PostgresSaver(pg_conn)
        sqlite_loader = SQLiteLoader(connection)
        data = sqlite_loader.load_movies()
        postgres_saver.save_all_data(data)
