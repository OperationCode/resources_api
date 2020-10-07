FROM python:3.7-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_BINARY psycopg2
ENV FLASK_SKIP_DOTENV 1
ENV FLASK_APP run.py

WORKDIR /src

COPY pyproject.toml poetry.lock ./

RUN mkdir /static

RUN apt-get update \
    && apt-get install -y libpq-dev gcc libpcre3 libpcre3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false

RUN poetry install --no-dev --no-interaction --no-ansi

COPY . /src

RUN useradd -ms /bin/bash uwsgi

RUN mkdir /src

RUN chown -R uwsgi: . /src

USER uwsgi

EXPOSE 5000

CMD [ "uwsgi", "--ini", "app.ini" ]
