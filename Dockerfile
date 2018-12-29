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
    && pip install --upgrade pip

COPY Pipfile* /src/

RUN pip install pipenv \
    && pipenv install --system --skip-lock --deploy --dev

COPY . /src

EXPOSE 8000

CMD ["python", "run.py"]
