FROM python:3.12-slim

ARG MEROSS_EMAIL
ARG MEROSS_PASSWORD
ARG TELEGRAM_TOKEN

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libffi-dev

WORKDIR /app

RUN pip install pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy --ignore-pipfile

COPY plug-daemon.sh plug-daemon.sh
COPY plug-control.py plug-control.py
COPY state.txt state.txt

RUN chmod +x plug-daemon.sh

ENV MEROSS_EMAIL=${MEROSS_EMAIL}
ENV MEROSS_PASSWORD=${MEROSS_PASSWORD}
ENV TELEGRAM_TOKEN=${TELEGRAM_TOKEN}

ENTRYPOINT ["/app/plug-daemon.sh"]
