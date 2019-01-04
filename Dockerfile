FROM python:3.7-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_BINARY psycopg2

WORKDIR /src
RUN mkdir /static

RUN apt-get update \
    && apt-get install -y libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge -y --auto-remove gcc \
    && pip install --upgrade pip \
    && pip install alembic \
    && pip install psycopg2-binary \
    && pip install flake8 \
    && pip install Flask \
    && pip install Flask-Migrate \
    && pip install Flask-SQLAlchemy \
    && pip install SQLAlchemy \
    && pip install SQLAlchemy-Utils \
    && pip install PyYAML \
    && pip install flask-pytest \
    && pip install pytest \
    && pip install dataclasses \
    && pip install coverage \
    && pip install pytest-cov

COPY . /src

EXPOSE 8000

CMD ["python", "run.py"]
