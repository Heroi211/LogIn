FROM python:3.11-alpine
LABEL maintainer "Gabriel Drumond <gabriel_s4@hotmail.com>"
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
RUN sudo apt update && sudo apt upgrade && sudo apt add --no-cache build-base freetds openssl freetds-dev libressl-dev krb5-dev

COPY . /var/www
WORKDIR /var/www

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt

EXPOSE 8000
ENTRYPOINT python main.py

