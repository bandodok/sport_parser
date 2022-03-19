include deployment/remote/.env

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
	docker-compose -f deployment/dev/docker-compose-dev.yml -p sport_parser up --abort-on-container-exit



# docker images

app_build:
	docker build -f deployment/remote/Dockerfile -t bandodok/sport_parser_app:${TAG} .

app_push:
	docker push bandodok/sport_parser_app:${TAG}

# test server

deploy_test_app: init_server deploy_app

init_server:
	ansible-playbook deployment/remote/playbook.yml -i "${SERVER_IP}, " -u ${SERVER_USERNAME} -t init

deploy_app:
	SECRET_KEY="${SECRET_KEY}" \
    TAG=${TAG} \
    DEBUG=${DEBUG} \
    ALLOWED_HOSTS=${ALLOWED_HOSTS} \
    SERVER_IP=${SERVER_IP} \
    HOST_NAME=${HOST_NAME} \
    SERVER_USERNAME=${SERVER_USERNAME} \
    ADMIN_USERNAME=${ADMIN_USERNAME} \
    ADMIN_PASSWORD=${ADMIN_PASSWORD} \
    DB_NAME=${DB_NAME} \
    DB_USER=${DB_USER} \
    DB_PASSWORD=${DB_PASSWORD} \
    DB_HOST=${DB_HOST} \
    DB_PORT=${DB_PORT} \
    CHROMEDRIVER=${CHROMEDRIVER} \
    ROLLBAR_TOKEN=${ROLLBAR_TOKEN} \
    REDIS_HOST=${REDIS_HOST} \
	ansible-playbook deployment/remote/playbook.yml -i "${SERVER_IP}, " -u ${SERVER_USERNAME} --tags create_folders,create_test_env,copy_files

remove_db:
	ansible-playbook deployment/remote/playbook.yml -i "${SERVER_IP}, " -u ${SERVER_USERNAME} --tags remove_db

remove_app:
	ansible-playbook deployment/remote/playbook.yml -i "${SERVER_IP}, " -u ${SERVER_USERNAME} --tags remove_app

remove_all:
	ansible-playbook deployment/remote/playbook.yml -i "${SERVER_IP}, " -u ${SERVER_USERNAME} --tags remove_all



server_run:
	ssh ${SERVER_USERNAME}@${SERVER_IP} 'cd /home/sport_parser/app && sudo docker-compose -f docker-compose.yml pull'
	ssh ${SERVER_USERNAME}@${SERVER_IP} 'cd /home/sport_parser/app && sudo docker-compose -f docker-compose.yml up --build --remove-orphans --abort-on-container-exit'

server_stop:
	ssh ${SERVER_USERNAME}@${SERVER_IP} 'cd /home/sport_parser/app && sudo docker-compose -f docker-compose.yml down --volume'
