FROM python:3.7-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_BINARY psycopg2
ENV FLASK_SKIP_DOTENV 1
ENV FLASK_APP run.py

WORKDIR /src

ADD requirements.txt requirements.txt

RUN mkdir /static

RUN apt-get update \
    && apt-get install -y libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge -y --auto-remove gcc \
    && pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . /src

EXPOSE 5000

CMD ["flask", "run", "-h", "0.0.0.0"]
