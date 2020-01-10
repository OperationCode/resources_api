import pytest
from algoliasearch.exceptions import (AlgoliaException,
                                      AlgoliaUnreachableHostException)
from app import create_app
from app import db as _db
from app.utils import standardize_response
from configs import Config

TEST_DATABASE_URI = 'sqlite:///:memory:'

counter = 0


# TODO: session_app is not currently used because we need a
# persistent DB for all of our tests. It would be nice to take
# away the need for a persistent DB and be able to use this method again.
@pytest.fixture(scope='session')
def session_app(request):
    Config.SQLALCHEMY_DATABASE_URI = TEST_DATABASE_URI
    Config.TESTING = True
    app = create_app(Config)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


# TODO: session_db is not currently used because we need a
# persistent DB for all of our tests. It would be nice to take
# away the need for a persistent DB and be able to use this method again.
@pytest.fixture(scope='session')
def session_db(session_app, request):
    """Session-wide test database."""

    def teardown():
        _db.drop_all()

    _db.app = session_app
    _db.create_all()
    request.addfinalizer(teardown)
    return _db


# TODO: function_session is not currently used because we need a
# persistent DB for all of our tests. It would be nice to take
# away the need for a persistent DB and be able to use this method again.
@pytest.fixture(scope='function')
def function_session(session_db, request):
    """Creates a new database session for a test."""
    connection = session_db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = session_db.create_scoped_session(options=options)

    session_db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session


@pytest.fixture(scope='module')
def module_client():
    Config.SQLALCHEMY_DATABASE_URI = TEST_DATABASE_URI
    Config.TESTING = True
    flask_app = create_app(Config)

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


@pytest.fixture(scope='module')
def module_db():
    # Create the database and the database table
    _db.create_all()
    from app.cli import import_resources
    import_resources(_db)
    yield _db  # this is where the testing happens!

    _db.drop_all()


@pytest.fixture(scope='function')
def function_empty_db():
    # Create the database and the database table
    _db.create_all()
    yield _db  # this is where the testing happens!

    _db.drop_all()


@pytest.fixture(scope='function')
def fake_auth_from_oc(mocker):
    """
    Changes the return value of requests.post to be a custom response
    object so that we aren't validating external APIs in our unit tests
    """

    class ExternalApiRequest(object):
        @classmethod
        def post(cls):
            return FakeExternalResponse()

    class FakeExternalResponse(object):
        @classmethod
        def json(self):
            # The source code just checks that a value exists for 'token'
            # in the dict returned from the json method.
            return {'token': 'superlegittoken'}

    mocker.patch("requests.post", return_value=FakeExternalResponse())


@pytest.fixture(scope='function')
def fake_invalid_auth_from_oc(mocker):
    """
    Changes the return value of requests.post to be a custom response
    object so that we aren't validating external APIs in our unit tests
    """

    class ExternalApiRequest(object):
        @classmethod
        def post(cls):
            return FakeExternalResponse()

    class FakeExternalResponse(object):
        @classmethod
        def json(self):
            # Mock an error returned from the OC backend
            return {'error': 'Invalid Email or password.'}

    mocker.patch("requests.post", return_value=FakeExternalResponse())


@pytest.fixture(scope='function')
def fake_paginated_data_error(mocker):
    """
    Mocks an exception being raised during pagination to test error handling
    """

    def paginated_data():
        raise Exception("An \"unexpected\" Exception was raised!")

    mocker.patch('app.utils.Paginator.paginated_data', side_effect=paginated_data)


@pytest.fixture(scope='function')
def fake_commit_error(mocker):
    """
    Mocks an exception being raised during a db commit to test error handling
    """

    def commit():
        raise Exception("An \"unexpected\" Exception was raised!")

    mocker.patch('app.db.session.commit', side_effect=commit)


@pytest.fixture(scope='function')
def fake_key_query_error(mocker):
    """
    Mocks an exception being raised during a query to test error handling
    """

    mocker.patch('app.models.Key.query', new=None)


@pytest.fixture(scope='function')
def fake_algolia_save(mocker):
    """
    Mocks a save_object or partial_update_object call to algolia
    """

    mocker.patch(
        'algoliasearch.search_index.SearchIndex.save_object',
        return_value=None
    )
    mocker.patch(
        'algoliasearch.search_index.SearchIndex.partial_update_object',
        return_value=None
    )


@pytest.fixture(scope='function')
def fake_algolia_search(mocker):
    """
    Mocks a search call to algolia
    """

    def algolia_search(term, page_info):

        results = {
            'id': '0',
            'name': 'Mock',
            'url': term,
            'category': 'Mock',
            'languages': 'Mock',
            'paid': 'Mock',
            'notes': 'Mock',
            'upvotes': 0,
            'downvotes': 0,
            'times_clicked': 0,
            'created_at': 0,
            'last_updated': 0
        }

        return {'hits': [results],
                'page': page_info['page'],
                'nbPages': 2,
                'hitsPerPage': page_info['hitsPerPage'],
                'nbHits': 2}

    mocker.patch('algoliasearch.search_index.SearchIndex.search',
                 side_effect=algolia_search)


@pytest.fixture(scope='function')
def fake_algolia_unreachable_host(mocker):
    """
    Mocks calls to algolia with AlgoliaUnreachableHostException
    """
    def algolia_exception(*args):
        raise AlgoliaUnreachableHostException()

    mocker.patch('algoliasearch.search_index.SearchIndex.search',
                 side_effect=algolia_exception)
    mocker.patch('algoliasearch.search_index.SearchIndex.save_objects',
                 side_effect=algolia_exception)
    mocker.patch('algoliasearch.search_index.SearchIndex.partial_update_object',
                 side_effect=algolia_exception)


@pytest.fixture(scope='function')
def fake_algolia_exception(mocker):
    """
    Mocks calls to algolia with AlgoliaException
    """
    def algolia_exception(*args):
        raise AlgoliaException()

    mocker.patch('algoliasearch.search_index.SearchIndex.search',
                 side_effect=algolia_exception)
    mocker.patch('algoliasearch.search_index.SearchIndex.save_objects',
                 side_effect=algolia_exception)
    mocker.patch('algoliasearch.search_index.SearchIndex.partial_update_object',
                 side_effect=algolia_exception)


@pytest.fixture(scope='function')
def unmapped_standardize_response(mocker):
    """
    Mocks standardize_response called without a specific error
    """
    def response(*args):

        return standardize_response(dict(), 1337)

    mocker.patch('app.utils.standardize_response', return_value=response())
