include deployment/test/.env

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

celery_beat:
	celery -A sport_parser beat -l info



# dev app

run:
	python deployment/dev/sql_render.py > deployment/dev/_init.sql
	docker-compose -f deployment/dev/docker-compose.yml -p sport_parser up --abort-on-container-exit
