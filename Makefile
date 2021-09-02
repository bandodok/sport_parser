makemigrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

freeze:
	pip freeze > requirements.txt

shell:
	python manage.py shell_plus