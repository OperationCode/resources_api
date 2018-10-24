FROM python:3.7-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_BINARY psycopg2

WORKDIR /src
RUN mkdir /static

COPY Pipfile* /src/

RUN apt-get update \
    && apt-get install -y libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip
# incremental build so we don't have to redo the above.
RUN pip install pipenv \
    && pipenv install --system --deploy --dev \
    && apt-get purge -y --auto-remove gcc

COPY src /src


EXPOSE 8000

ENTRYPOINT ["flask"]
