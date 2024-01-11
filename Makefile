migrate:
	python manage.py makemigrations
	python manage.py migrate
	DJANGO_SUPERUSER_USERNAME=admin DJANGO_SUPERUSER_EMAIL=admin@example.com DJANGO_SUPERUSER_PASSWORD=password python manage.py createsuperuser --noinput

celery:
	celery -A weops_lite worker -B --loglevel=info

run:
	daphne -b 0.0.0.0 -p 8000 weops_lite.asgi:application

test:
	pytest

show_test_result:
	allure serve ./allure-results


