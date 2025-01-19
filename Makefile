remigrate:
	find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
	python3 manage.py makemigrations --empty --name initial izr_media
	python3 manage.py makemigrations --empty --name initial izr_products
	python3 manage.py makemigrations --empty --name initial izr_school
	python3 manage.py makemigrations --empty --name initial izr_staff
	python3 manage.py migrate --fake-initial
.PHONY: start

start:
	@echo "Waiting for MySQL to be ready..."
	@while ! nc -z sql 3306; do \
	    sleep 1; \
	done
	@echo "MySQL is up - running migrations"
	python manage.py migrate --noinput
	python manage.py collectstatic --noinput
	gunicorn izr_server.wsgi:application --bind 0.0.0.0:8000