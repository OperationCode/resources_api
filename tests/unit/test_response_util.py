import pytest
from flask import Flask, Response

from app.versioning import LATEST_API_VERSION
from app.utils import standardize_response


def test_presents_requested_api_version(app, client):
    @app.route('/endpoint')
    def endpoint():
        return standardize_response({})

    response: Response = client.get('/endpoint', headers=[('X-API-Version', '1.8')])

    assert response.json['apiVersion'] == 1.8


def test_defaults_to_fallback_api_version_when_none_specified(app, client):
    @app.route('/endpoint')
    def endpoint():
        return standardize_response({})

    response: Response = client.get('/endpoint')

    expected_version = float(LATEST_API_VERSION)
    assert response.json['apiVersion'] == expected_version


@pytest.fixture
def app():
    return Flask(__name__)


@pytest.fixture
def client(app):
    return app.test_client()
