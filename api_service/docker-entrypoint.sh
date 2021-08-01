#!/usr/bin/env bash

echo "Elastic is not running..."

while ! nc -z "$ELASTIC_HOST" "$ELASTIC_PORT"; do
  sleep 0.1
done

echo "Elastic is running"

echo "Redis is not running..."

while ! nc -z "$REDIS_HOST" "$REDIS_PORT"; do
  sleep 0.1
done

echo "Redis is running"

exec "$@"