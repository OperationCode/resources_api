from unittest.mock import patch

from app.api.auth import (ApiKeyError, ApiKeyErrorCode, authenticate,
                          blacklist_key, find_key_by_apikey_or_email)
from app.models import Key

FAKE_EMAIL = 'test@example.org'
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
    key = Key(email=FAKE_EMAIL, apikey=FAKE_APIKEY)
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
    key = Key(email=FAKE_EMAIL, apikey=FAKE_APIKEY, blacklisted=True)
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


def test_find_key_by_apikey_or_email(module_client, module_db):
    # Arrange
    key = Key(email=FAKE_EMAIL, apikey=FAKE_APIKEY)
    module_db.session.add(key)

    # Act
    key1 = find_key_by_apikey_or_email(FAKE_EMAIL)
    key2 = find_key_by_apikey_or_email(FAKE_APIKEY)

    # Assert
    assert key == key1
    assert key == key2

    module_db.session.rollback()


def test_blacklist_key_not_found(module_client, module_db):
    # Arrange
    error = None

    # Act
    try:
        blacklist_key(FAKE_APIKEY + 'b', True)
    except ApiKeyError as e:
        error = e

    # Assert
    assert error.error_code == ApiKeyErrorCode.NOT_FOUND


def test_blacklist_key_already_blacklisted(module_client, module_db):
    # Arrange
    error = None
    key1 = None
    key = Key(email=FAKE_EMAIL, apikey=FAKE_APIKEY, blacklisted=True)
    module_db.session.add(key)

    # Act
    try:
        key1 = blacklist_key(FAKE_APIKEY, True)
    except ApiKeyError as e:
        error = e

    # Assert
    assert error.error_code == ApiKeyErrorCode.ALREADY_BLACKLISTED
    assert key1 is None

    module_db.session.rollback()


def test_blacklist_key_not_blacklisted(module_client, module_db):
    # Arrange
    error = None
    key1 = None
    key = Key(email=FAKE_EMAIL, apikey=FAKE_APIKEY)
    module_db.session.add(key)

    # Act
    try:
        key1 = blacklist_key(FAKE_APIKEY, False)
    except ApiKeyError as e:
        error = e

    # Assert
    assert error.error_code == ApiKeyErrorCode.NOT_BLACKLISTED
    assert key1 is None

    module_db.session.rollback()


def test_blacklist_key_set_blacklisted_on(module_client, module_db):
    # Arrange
    key = Key(email=FAKE_EMAIL, apikey=FAKE_APIKEY)
    module_db.session.add(key)

    # Act
    key1 = blacklist_key(FAKE_APIKEY, True)

    # Assert
    assert key.blacklisted
    assert key == key1

    module_db.session.rollback()


def test_blacklist_key_set_blacklisted_off(module_client, module_db):
    # Arrange
    key = Key(email=FAKE_EMAIL, apikey=FAKE_APIKEY, blacklisted=True)
    module_db.session.add(key)

    # Act
    key1 = blacklist_key(FAKE_APIKEY, False)

    # Assert
    assert not key.blacklisted
    assert key == key1

    module_db.session.rollback()
