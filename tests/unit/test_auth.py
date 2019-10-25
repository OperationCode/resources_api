from unittest.mock import patch

from app.api.auth import authenticate
from app.models import Key

FAKE_APIKEY = 'abcdef1234567890'


def test_authenticate_failure(module_client, module_db):
    # Arrange
    def callback(*args, **kwargs):
        return 1

    # Act
    wrapper = authenticate(callback)
    with patch('app.api.auth.request') as fake_request:
        fake_request.headers = {
            'x-apikey': FAKE_APIKEY
        }
        result = wrapper()

    # Assert
    assert result[1] == 401


def test_authenticate_success(module_client, module_db):
    # Arrange
    key = Key(email="test@example.org", apikey=FAKE_APIKEY)
    module_db.session.add(key)

    def callback(*args, **kwargs):
        return 1

    # Act
    wrapper = authenticate(callback)
    with patch('app.api.auth.request') as fake_request:
        fake_request.headers = {
            'x-apikey': FAKE_APIKEY
        }
        result = wrapper()

    # Assert
    assert result == 1

    module_db.session.rollback()


def test_authenticate_blacklisted(module_client, module_db):
    # Arrange
    key = Key(email="test@example.org", apikey=FAKE_APIKEY, blacklisted=True)
    module_db.session.add(key)

    def callback(*args, **kwargs):
        return 1

    # Act
    wrapper = authenticate(callback)
    with patch('app.api.auth.request') as fake_request:
        fake_request.headers = {
            'x-apikey': FAKE_APIKEY
        }
        result = wrapper()

    # Assert
    assert result[1] == 401

    module_db.session.rollback()
