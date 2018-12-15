import os
import tempfile
import pytest
from app import create_app

TESTDB = 'test_project.db'
TESTDB_PATH = "tests/data/{}".format(TESTDB)
TEST_DATABASE_URI = 'sqlite:///' + TESTDB_PATH


ALEMBIC_CONFIG = 'migrations/alembic.ini'


@pytest.fixture(scope='module')
def app():
    app = create_app()
    app.testing = True
    return app

@pytest.fixture(scope='module')
def client(app):
    client = app.test_client()
    return client
