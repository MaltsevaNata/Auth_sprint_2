import sqlite3
from typing import Optional, List

from .sqlite_schema_class import *


class SQLiteLoader:
    def __init__(self, connection):
        self.conn = connection
        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()
        self.movies = []

    def convert_to_float(self, num) -> Optional[float]:
        """Если передана строка с числом, то преобразует ее в тип float"""
        try:
            return float(num)
        except ValueError:
            return None

    def get_names(self, rows) -> Set:
        """Возвращает все уникальные имена людей из строк"""
        names = set()
        for row in rows:
            row = dict(row)
            if row["name"] != "N/A":
                names.add(row["name"])
        return names

    def load_movies(self) -> List[MovieFromSqlite]:
        """Выгружает данные о фильмах из SQlite и возращает в виде списка объектов Movie_from_sqlite"""
        self.c.execute("SELECT * FROM movies ORDER BY id")
        movies_rows = self.c.fetchall()
        for movie in movies_rows:
            movie = dict(movie)
            directors = set(movie['director'].split(', ') if movie['director'] != 'N/A' else [])
            genres = set(movie['genre'].split(', ') if movie['genre'] != 'N/A' else [])
            description = movie['plot'] if movie['plot'] != "N/A" else None
            command = f"""SELECT A.id, A.name FROM actors A INNER JOIN movie_actors MA ON MA.actor_id = A.id AND 
                      MA.movie_id = '{movie['id']}'"""
            self.c.execute(command)
            actors_rows = self.c.fetchall()
            actors = self.get_names(actors_rows)
            command = f"""SELECT W.id, W.name FROM writers W INNER JOIN movies M ON M.writer = W.id OR M.writers 
                      LIKE '%'||W.id||'%' WHERE M.id = '{movie['id']}'"""
            self.c.execute(command)
            writers_rows = self.c.fetchall()
            writers = self.get_names(writers_rows)
            parsed_movie = MovieFromSqlite(id=movie['id'], imdb_rating=self.convert_to_float(movie['imdb_rating']),
                                           genres=genres,
                                           title=movie['title'], description=description, directors=directors,
                                           actors=actors, writers=writers)
            self.movies.append(parsed_movie)
        return self.movies
