from datetime import datetime, timezone, timedelta
import json
import time
import logging
from typing import Callable

from elasticsearch import Elasticsearch, exceptions, helpers
import psycopg2
import backoff
from psycopg2.extras import DictCursor

from .state_class import JsonFileStorage, State
from models.filmwork import FilmWork
from models.genre import Genre
from models.person import Person
from .coroutine import coroutine
from .queries import movies_query, genres_query, persons_query


class ETL:
    def __init__(self, file_path: str, pg_conn: psycopg2.connect, es_url: str, dsl: dict):
        self.conn = pg_conn
        self.cursor = self.conn.cursor()
        self.dsl = dsl
        self.main_tables = ('movies_person', 'movies_genre', 'movies_filmwork')
        self.associated_tables = ('movies_filmwork_genres', 'movies_personrole')
        self.storage = JsonFileStorage(file_path)
        self.postgresState = State(self.storage)
        self.es = Elasticsearch(es_url)
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger('backoff').addHandler(logging.StreamHandler())

    @backoff.on_exception(backoff.expo, (exceptions.ConnectionError, exceptions.ConnectionTimeout))
    def clear_index_data(self, index_name: str):
        """
        очищает все данные внутри индекса. Это нужно, потому что при запуске всей системы индексы
        в postgres генерируются заново, и использовать существующие записи в es не удастся
        """
        self.es.indices.delete(index=index_name, ignore=404)
        self.es.indices.create(index=index_name)

    def initial_update(self):
        """
        заносит все записи из Postgres в ES и устанавливает время обновления
        """
        logging.warning('Wait while all data will be loaded to ES...')
        self.clear_index_data('movies')
        self.clear_index_data('genres')
        self.clear_index_data('persons')
        updater = self.update_es()
        transform = self.transform_received(updater)
        self.initial_load_from_psql(transform)
        updater.close()
        transform.close()
        cur_time = (datetime.now(timezone.utc)).strftime("%m-%d-%Y %H:%M:%S")
        for table_name in self.main_tables:
            self.postgresState.set_state(table_name, cur_time)
        logging.warning('Now ES is up-to-date with postgres')

    def initial_load_from_psql(self, target: Callable):
        """
        выгружает все записи из Postgres пачками и отправляет обработчику
        """
        @backoff.on_exception(backoff.expo, psycopg2.Error)
        def load(self, target):
            queries = [{'index': 'genres', 'query': genres_query}, {'index': 'movies', 'query': movies_query},
                       {'index': 'persons', 'query': persons_query}]
            for query in queries:
                offset = 0
                while True:
                    q = query['query'](offset)
                    self.cursor.execute(q)
                    offset += 100
                    all_rows = [dict(row) for row in self.cursor]
                    target.send({'index': query['index'], 'data': all_rows})
                    if len(all_rows) < 100:
                        break
        load(self, target)

    @backoff.on_exception(backoff.expo, (exceptions.ConnectionError, exceptions.ConnectionTimeout))
    def update_es_instances(self, index: str, data: list):
        """
        Обновляет пачку записей в индексе в es
        """
        logging.warning(f"""Updating {index} in ES""")
        doc_data = [{
            "_op_type": 'update',
            "_type": "_doc",
            "_index": index,
            "_id": instance.id,
            "doc": instance.dict(),
            "doc_as_upsert": True
        } for instance in data]
        helpers.bulk(self.es, doc_data)

    @coroutine
    def update_es(self):
        """
        обновляет записи в ES или добавляет, если их нет
        """
        while True:
            instances_to_update = (yield)
            self.update_es_instances(instances_to_update['index'], instances_to_update['data'])

    @coroutine
    def transform_received(self, target: Callable):
        """
        приводит записи из Postgres к пригодной для ES структуре
        """
        roles_correlation = {'director': 'directors', 'actor': 'actors', 'scriptwriter': 'writers'}
        while True:
            rows = (yield)
            index = rows['index']
            rows = rows['data']
            data = []
            for row in rows:
                if index == 'movies':
                    fw_id = row['fw_id']
                    filmwork = next((item for item in data if item.id == fw_id), False)
                    if not filmwork:
                        data.append(FilmWork(id=row['fw_id'], title=row['title'], imdb_rating=row["rating"],
                                                       description=row['description']))
                        filmwork = data[-1]
                    role_name = row['role']
                    if role_name:
                        role_field_name = roles_correlation[row['role']]
                        role_field_value = getattr(filmwork, role_field_name)
                        name = f"""{row['first_name']} {row['last_name']}"""
                        if not name in role_field_value:
                            role_field_value.append(name)
                        setattr(filmwork, role_field_name, role_field_value)
                    genre = {"name": row["name"], "id": row["g_id"]}
                    if not genre in filmwork.genres:
                        filmwork.genres.append(genre)
                elif index == 'genres':
                    genre = next((item for item in data if item.id == row["g_id"]), False)
                    if not genre:
                        data.append(Genre(id=row['g_id'], name=row['name']))
                        genre = data[-1]
                    fw_id = row["fw_id"]
                    if not fw_id in genre.filmworks:
                        genre.filmworks.append(fw_id)

                elif index == 'persons':
                    person = next((item for item in data if item.id == row["p_id"]), False)
                    if not person:
                        data.append(Person(id=row['p_id'], first_name=row['first_name'], last_name=row['last_name']))
                        person = data[-1]
                    fw_id = row["fw_id"]
                    role = row["person_role"]
                    if not fw_id in person.film_ids:
                        person.film_ids.append(fw_id)
                    if not role in person.role:
                        person.role.append(role)

            target.send({'index': index, 'data': data})

    @coroutine
    def get_associated_instances(self, target: Callable):
        """
        делает JOIN остальных таблиц, связанных с данной записью
        """
        references = [{'table_name': 'movies_person', 'join_table_name': 'movies_personrole', 'field': 'person_id'},
                       {'table_name': 'movies_genre', 'join_table_name': 'movies_filmwork_genres', 'field': 'genre_id'},
                       {'table_name': 'movies_filmwork', 'join_table_name': None, 'field': None}]

        @backoff.on_exception(backoff.expo, psycopg2.Error, on_backoff=self.postgres_backoff_handler)
        def join_all_fw_tables(self, fw_ids: list, target: Callable):
            # поиск всех связанных записей из других таблиц
            self.cursor.execute(f"""SELECT
                                            fw.id as fw_id, 
                                            fw.title, 
                                            fw.description, 
                                            fw.rating, 
                                            fw.filmwork_type, 
                                            fw.created, 
                                            fw.modified, 
                                            pfw.role, 
                                            p.id, 
                                            p.first_name,
                                            p.last_name,
                                            g.name,
                                            g.id as g_id
                                        FROM movies_filmwork fw
                                        LEFT JOIN movies_personrole pfw ON pfw.filmwork_id = fw.id
                                        LEFT JOIN movies_person p ON p.id = pfw.person_id
                                        LEFT JOIN movies_filmwork_genres gfw ON gfw.filmwork_id = fw.id
                                        LEFT JOIN movies_genre g ON g.id = gfw.genre_id
                                        WHERE fw.id IN {fw_ids};""")
            all_rows = [dict(row) for row in self.cursor]
            target.send({'index': 'movies', 'data': all_rows})

        @backoff.on_exception(backoff.expo, psycopg2.Error, on_backoff=self.postgres_backoff_handler)
        def join_genres_persons_tables(self, table_name: str, ids: list, target: Callable):
            if table_name == 'movies_genre':
                self.cursor.execute(f"""SELECT
                                                g.name,
                                                g.id as g_id,
                                                fw.id as fw_id
                                        FROM movies_genre g
                                        LEFT JOIN movies_filmwork_genres gfw ON gfw.genre_id = g.id
                                        LEFT JOIN movies_filmwork fw ON fw.id = gfw.filmwork_id
                                        WHERE g.id IN {ids};""")
                all_rows = [dict(row) for row in self.cursor]
                target.send({'index': 'genres', 'data': all_rows})
            elif table_name == 'movies_person':
                self.cursor.execute(f"""SELECT
                                                p.first_name,
                                                p.last_name,
                                                p.id as p_id,
                                                fw.id as fw_id,
                                                pfw.role as person_role
                                        FROM movies_person p
                                        LEFT JOIN movies_personrole pfw ON pfw.person_id = p.id
                                        LEFT JOIN movies_filmwork fw ON fw.id = pfw.filmwork_id
                                        WHERE p.id IN {ids};""")
                all_rows = [dict(row) for row in self.cursor]
                target.send({'index': 'persons', 'data': all_rows})

        @backoff.on_exception(backoff.expo, psycopg2.Error, on_backoff=self.postgres_backoff_handler())
        def get_associated_movies(self, reference: dict, ids: list):
            """
            поиск всех фильмов, связанных с данной записью
            """
            sql_query = f"""SELECT fw.id, fw.modified
                                FROM movies_filmwork fw
                                LEFT JOIN {reference['join_table_name']} pfw ON pfw.filmwork_id = fw.id
                                WHERE pfw.{reference['field']} IN {ids}
                                ORDER BY fw.modified DESC
                                LIMIT 100;"""
            self.cursor.execute(sql_query)
            dict_cur = (dict(row) for row in self.cursor)
            fw_ids = tuple([item['id'] for item in dict_cur])
            if len(fw_ids) == 0:
                return None
            if len(fw_ids) == 1:
                fw_ids = f"""('{fw_ids[0]}')"""
            return fw_ids

        while True:
            table_name, ids, time = (yield)
            if len(ids) == 1:
                ids = f"""('{ids[0]}')"""
            if table_name == 'movies_filmwork':
                fw_ids = ids
            else:
                join_genres_persons_tables(self, table_name, ids, target)
                reference = next(item for item in references if item['table_name'] == table_name)
                fw_ids = get_associated_movies(self, reference, ids)
                if fw_ids is None:
                    continue
            join_all_fw_tables(self, fw_ids, target)

    def postgres_backoff_handler(self, *args, **kwargs):
        self.reconnect_postgres()

    def reconnect_postgres(self):
        self.conn = psycopg2.connect(
            **self.dsl, cursor_factory=DictCursor)
        self.cursor = self.conn.cursor()

    def get_last_table_updates(self, table_name: str, target: Callable):
        """
        поиск последних изменений в этой таблице
        """
        try:
            update_time_str = self.postgresState.state[table_name]
            update_time = datetime.strptime(update_time_str, "%m-%d-%Y %H:%M:%S")
            self.cursor.execute(f"""SELECT id, modified
                                    FROM {table_name}
                                    WHERE modified > '{update_time}'
                                    ORDER BY modified DESC
                                    LIMIT 100;""")
            dict_cur = (dict(row) for row in self.cursor)
        except psycopg2.Error as e:
            print(e)
            logging.warning("Waiting for Postgres to wake up...")
            try:
                self.reconnect_postgres()
            except psycopg2.Error as e:
                pass
            return
        modified = []
        ids = []
        for item in dict_cur:
            ids.append(item['id'])
            modified.append(item['modified'])
        if len(ids) > 0:
            update_time = modified[0]
            update_time = update_time + timedelta(seconds=2)
            update_time_str = update_time.strftime("%m-%d-%Y %H:%M:%S")
            self.postgresState.set_state(table_name, update_time_str)
            ids = tuple(ids)
            info_to_send = (table_name, ids, update_time)
            target.send(info_to_send)

    def get_updated_instances(self, target: Callable):
        """
        Поиск записей, измененных после последнего обновления состояния
        """
        while True:
            for table_name in self.main_tables:
                self.get_last_table_updates(table_name, target)
            time.sleep(2)

    def start_merge(self):
        """
        запуск бесконечного цикла обновления данных из Postgres в ES
        """
        updater = self.update_es()
        transform = self.transform_received(updater)
        associated_loader = self.get_associated_instances(transform)
        self.get_updated_instances(associated_loader)



