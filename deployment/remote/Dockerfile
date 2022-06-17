FROM python:3.10

WORKDIR /home/bandodok/sport_parser
COPY ./requirements.txt /home/bandodok/sport_parser/requirements.txt
RUN apt update && apt install netcat -y && python -m pip install --upgrade pip && python -m pip install -r requirements.txt
COPY . /home/bandodok/sport_parser/