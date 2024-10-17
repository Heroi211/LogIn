FROM postgres:16.2-alpine
LABEL maintainer "Gabriel Drumond <gabriel.drumond@cod3bit.com.br>"
ENV POSTGRES_USER=hero
ENV POSTGRES_PASSWORD=280387
ENV POSTGRES_DB=login
EXPOSE 5432