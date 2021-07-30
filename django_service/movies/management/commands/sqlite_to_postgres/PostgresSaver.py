from typing import List, Any, get_type_hints

import psycopg2.extras

from .postgres_schema_classes import *
from .sqlite_schema_class import MovieFromSqlite


class PostgresSaver:
    def __init__(self, pg_conn: psycopg2.connect):
        psycopg2.extras.register_uuid()
        self.conn = pg_conn
        self.cursor = self.conn.cursor()
        self.tables = ('movies_filmwork', 'movies_filmwork_genres', 'movies_filmwork_persons',
                       'movies_genre', 'movies_person', 'movies_personrole')
        self.clear_tables()
        self.genres = []
        self.people = []

    def clear_tables(self) -> None:
        """Удаляет все строки из всех таблиц Postgres."""
        for table in self.tables:
            self.cursor.execute(f"""TRUNCATE {table}""")

    def add_person(self, name: str, role: str, filmwork: Filmwork, filmwork_persons: List[FilmworkPersons],
                   new_people: List[Person], personroles: List[PersonRole]) -> None:
        """Создает сущность Person и зависимости PersonRole и Filmwork_persons для нее"""
        first, *last = name.split()
        last = " ".join(last).replace('co-director', '')
        person = next((x for x in self.people if x.first_name == first and x.last_name == last), False)
        if not person:
            person = Person(first_name=first, last_name=last)
            self.people.append(person)
            new_people.append(person)
        filmwork_person = FilmworkPersons(filmwork_id=filmwork.id, person_id=person.id)
        filmwork_persons.append(filmwork_person)
        personrole = PersonRole(person_id=person.id, filmwork_id=filmwork.id, role=role)
        personroles.append(personrole)

    def ordered_values(self, fields: List[str], item: Any) -> List[Any]:
        """Возвращает список значений по порядку полей в fields"""
        values = []
        for field in fields:
            values.append(getattr(item, field))
        return values

    def insert_in_table(self, table_name: str, fields: List[str], instances: List[Any]) -> None:
        """Множественная вставка строк в таблицу"""
        if len(instances) > 0:
            string_token = ('%s, ' * len(fields)).rstrip(', ')
            string_token = f"""({string_token})"""
            args = ','.join(self.cursor.mogrify(string_token, self.ordered_values(fields, item)).decode()
                            for item in instances)
            fields_str = '(' + ', '.join(fields) + ')'
            self.cursor.execute(f"""INSERT INTO {table_name} {fields_str} VALUES {args}""")

    def prepare_and_load_movie_data(self, movie_from_sqlite: MovieFromSqlite) -> None:
        """Преобразование структуры данных фильма из SQlite в структуру для Postgres и загрузка в таблицы Postgres"""
        new_people, new_genres, filmworks, filmwork_genres, filmwork_persons, personroles = ([] for i in range(6))
        filmwork = Filmwork(title=movie_from_sqlite.title, description=movie_from_sqlite.description,
                            rating=movie_from_sqlite.imdb_rating)
        filmworks.append(filmwork)
        for genre_str in movie_from_sqlite.genres:
            genre = next((x for x in self.genres if x.name == genre_str), False)
            if not genre:
                genre = Genre(name=genre_str)
                self.genres.append(genre)
                new_genres.append(genre)
            filmwork_genre = FilmworkGenres(filmwork_id=filmwork.id, genre_id=genre.id)
            filmwork_genres.append(filmwork_genre)

        for person_role, persons in (('scriptwriter', movie_from_sqlite.writers), ('actor', movie_from_sqlite.actors),
                                     ('director', movie_from_sqlite.directors)):
            for person in persons:
                self.add_person(person, person_role, filmwork, filmwork_persons, new_people, personroles)

        self.insert_in_table('movies_filmwork', [*get_type_hints(Filmwork)], filmworks)  # '*' to get dict keys
        self.insert_in_table('movies_genre', [*get_type_hints(Genre)], new_genres)
        self.insert_in_table('movies_filmwork_genres', [*get_type_hints(FilmworkGenres)], filmwork_genres)
        self.insert_in_table('movies_person', [*get_type_hints(Person)], new_people)
        self.insert_in_table('movies_filmwork_persons', [*get_type_hints(FilmworkPersons)], filmwork_persons)
        self.insert_in_table('movies_personrole', [*get_type_hints(PersonRole)], personroles)

    def save_all_data(self, data: List[MovieFromSqlite]) -> None:
        """Подготавливает данные всех фильмов для загрузки и загружает в Postgres"""
        for movie_from_sqlite in data:
            self.prepare_and_load_movie_data(movie_from_sqlite)
