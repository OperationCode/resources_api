import os
import tempfile
import pytest
import tempfile
from app import db
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
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()

    app.config['SQLALCHEMY_DATABASE_URI'] = TEST_DATABASE_URI

    with app.app_context():
        db.create_all()

    client = app.test_client()

    yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])