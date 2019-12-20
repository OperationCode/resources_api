import pytest
from flask import Flask, Response

from app.versioning import versioned, LATEST_API_VERSION, InvalidApiVersion


@pytest.mark.parametrize('versions', ['1.4', '1.4.1-snapshot'])
def test_passes_valid_version_from_api_header_to_wrapped_route(app, client, versions):
    @app.route('/endpoint')
    @versioned(valid_versions=[versions])
    def endpoint(version: str):
        return dict(version=version)

    response: Response = client.get('/endpoint', headers=[('X-Api-Version', versions)])

    assert response.json == dict(version=versions)


def test_defaults_to_latest_api_version_when_api_header_is_not_passed(app, client):
    @app.route('/endpoint')
    @versioned
    def endpoint(version: str):
        return dict(version=version)

    response: Response = client.get('/endpoint')

    expected_version = LATEST_API_VERSION
    assert response.json == dict(version=expected_version)


@pytest.mark.parametrize('header_value', ('99.99', 'i-am-a-monkey', '1.2.0-alpha.1'))
def test_throws_exception_when_invalid_version_passed_in_api_header(
        app, client, header_value):
    @app.route('/endpoint')
    @versioned
    def endpoint(version: str):
        return dict(version=version)

    @app.errorhandler(InvalidApiVersion)
    def handle_exception(exception: InvalidApiVersion):
        return exception.description, exception.code

    response: Response = client.get(
        '/endpoint', headers=[('X-API-Version', header_value)])

    response_text = str(response.data, 'utf-8')
    assert (response_text == InvalidApiVersion(header_value).description
            and response.status_code == 400)


def test_does_not_throw_exception_on_invalid_version_when_told_not_to(app, client):
    @app.route('/endpoint')
    @versioned(throw_on_invalid=False)
    def endpoint(version: str):
        return dict(version=version)

    response: Response = client.get('/endpoint', headers=[('X-API-Version', 'bob')])

    assert response.json == dict(version=LATEST_API_VERSION)


@pytest.fixture
def app():
    return Flask(__name__)


@pytest.fixture
def client(app):
    return app.test_client()
