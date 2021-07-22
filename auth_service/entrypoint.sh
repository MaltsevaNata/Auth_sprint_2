#!/bin/sh

python3 ./utils/wait_for_redis.py
python3 ./utils/wait_for_pg.py
gunicorn wsgi_app:app -c gunicorn.conf.py
exec "$@"
