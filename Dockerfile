FROM python:latest

LABEL maintainer="Grega Vrbančič <grega.vrbancic@gmail.com"

ENV DOCKER=true

WORKDIR /app

COPY pyproject.toml .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry install

EXPOSE 8000