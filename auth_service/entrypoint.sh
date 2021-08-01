#!/bin/sh

python3 ./utils/wait_for_redis.py
python3 ./utils/wait_for_pg.py
flask db upgrade
gunicorn -c gunicorn_conf.py wsgi_app:app --reload
exec "$@"
