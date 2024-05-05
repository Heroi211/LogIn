FROM python:3.11.2
LABEL maintainer "Gabriel Drumond <gabriel_s4@hotmail.com>"
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
RUN apk update && apk add --no-cache build-base freetds openssl freetds-dev libressl-dev krb5-dev

COPY . /repositorios/LogIn
WORKDIR /var/www

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt

ENTRYPOINT python main.py runserver 0.0.0.0:8000
EXPOSE 8000
