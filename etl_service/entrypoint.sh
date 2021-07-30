#!/bin/sh

echo "Waiting for psql and es to start..."

while ! nc -z "$SQL_HOST" "$SQL_PORT"; do
      sleep 0.1
done
echo "PostgreSQL started"

while ! nc -z "$ELASTIC_HOST" "$ELASTIC_PORT"; do
  sleep 0.1
done
echo "ES started"
cd src
python main.py

exec "$@"