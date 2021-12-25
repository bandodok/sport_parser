makemigrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

freeze:
	pip freeze > requirements.txt

shell:
	python manage.py shell_plus

celery:
	celery -A sport_parser worker -l info -P eventlet --concurrency=1