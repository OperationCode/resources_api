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
    && pip install --upgrade pip \
    && pip install python-dotenv \
    && pip install flask \
    && pip install flask_migrate \
    && pip install SQLAlchemy-Utils
# incremental build so we don't have to redo the above.
RUN pip install pipenv \
    && pipenv install --deploy --dev \
    && apt-get purge -y --auto-remove gcc

COPY . /src


EXPOSE 8000


ENTRYPOINT ["python", "run.py"]
CMD ["python", "-m", "flask", "run"]
