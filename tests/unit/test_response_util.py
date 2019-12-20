import pytest
from flask import Flask, Response

from app.versioning import LATEST_API_VERSION, VALID_API_VERSIONS
from app.utils import standardize_response


def test_presents_requested_api_version(app, client):
    @app.route('/endpoint')
    def endpoint():
        return standardize_response({})

    api_version = VALID_API_VERSIONS[0]
    response: Response = client.get(
        '/endpoint', headers=[('X-API-Version', api_version)])

    assert response.json['apiVersion'] == api_version


def test_defaults_to_fallback_api_version_when_none_specified(app, client):
    @app.route('/endpoint')
    def endpoint():
        return standardize_response({})

    response: Response = client.get('/endpoint')

    expected_version = LATEST_API_VERSION
    assert response.json['apiVersion'] == expected_version


def test_defaults_to_fallback_api_version_when_invalid_one_is_specified(app, client):
    @app.route('/endpoint')
    def endpoint():
        return standardize_response({})

    response: Response = client.get('/endpoint', headers=[('X-API-Version', 'sue')])

    expected_version = LATEST_API_VERSION
    assert response.json['apiVersion'] == expected_version


@pytest.fixture
def app():
    return Flask(__name__)


@pytest.fixture
def client(app):
    return app.test_client()
