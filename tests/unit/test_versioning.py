import pytest
from flask import Flask, Response

from app.api.versioning import versioned, DEFAULT_VERSION


def test_passes_version_specified_in_correct_header_to_wrapped_route(app, client):
    @app.route('/endpoint')
    @versioned
    def endpoint(version: float):
        return dict(version=version)

    response: Response = client.get('/endpoint', headers=[('X-Api-Version', '1.4')])

    assert response.json == dict(version=1.4)


def test_defaults_to_app_version_when_correct_header_is_not_passed(app, client):
    @app.route('/endpoint')
    @versioned
    def endpoint(version: float):
        return dict(version=version)

    response: Response = client.get('/endpoint')

    expected_version = float(DEFAULT_VERSION)
    assert response.json == dict(version=expected_version)


@pytest.fixture
def app():
    return Flask(__name__)


@pytest.fixture
def client(app):
    return app.test_client()
