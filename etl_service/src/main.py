import os

from psycopg2.extras import DictCursor
import psycopg2

from services.ETL import ETL

if __name__ == '__main__':
    dsl = {'dbname': os.environ['SQL_DATABASE'], 'user': os.environ['SQL_USER'], 'password': os.environ['SQL_PASSWORD'],
           'host': os.environ['SQL_HOST'], 'port': os.environ['SQL_PORT']}
    with psycopg2.connect(
                **dsl, cursor_factory=DictCursor) as pg_conn:
        es_host = os.environ['ELASTIC_HOST']
        es_port = os.environ['ELASTIC_PORT']
        mergePipe = ETL(file_path='state.json', pg_conn=pg_conn, es_url=f"http://{es_host}:{es_port}/", dsl=dsl)
        mergePipe.initial_update()
        mergePipe.start_merge()