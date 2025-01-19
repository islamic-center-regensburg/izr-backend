#!/bin/sh

echo "Waiting for MySQL to be ready..."

while ! nc -z sql 3306; do
  sleep 1
done

echo "MySQL is up - running migrations"

python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn izr_server.wsgi:application --bind 0.0.0.0:8000s