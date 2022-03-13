import jinja2
import dotenv
from os.path import join, dirname
import os


if __name__ == '__main__':
    env_path = join(dirname(__file__), '.env')
    dotenv.load_dotenv(env_path)
    with open('deployment/init.sql.j2', 'r') as file:
        template = jinja2.Template(file.read())
        print(template.render(
            DB_USER=os.getenv('DB_USER'),
            DB_PASSWORD=os.getenv('DB_PASSWORD'),
            DB_NAME=os.getenv('DB_NAME')
        ))
