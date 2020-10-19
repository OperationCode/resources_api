from unittest.mock import patch

from app.api.auth import (ApiKeyError, ApiKeyErrorCode, authenticate,
                          deny_key, find_key_by_apikey_or_email,
                          rotate_key)
from tests.utils import create_fake_key, FAKE_EMAIL, FAKE_APIKEY
from flask import g


def test_authenticate_failure(module_client, function_empty_db):
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


def test_authenticate_success(module_client, function_empty_db):
    # Arrange
    key = create_fake_key(function_empty_db.session)

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
    assert g.auth_key == key


def test_authenticate_denied(module_client, function_empty_db):
    # Arrange
    create_fake_key(function_empty_db.session, denied=True)

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


def test_find_key_by_apikey_or_email(module_client, function_empty_db):
    # Arrange
    key = create_fake_key(function_empty_db.session)

    # Act
    key1 = find_key_by_apikey_or_email(FAKE_EMAIL)
    key2 = find_key_by_apikey_or_email(FAKE_APIKEY)

    # Assert
    assert key == key1
    assert key == key2


def test_denied_key_not_found(module_client, function_empty_db):
    # Arrange
    error = None

    # Act
    try:
        deny_key(FAKE_APIKEY + 'b', True, function_empty_db.session)
    except ApiKeyError as e:
        error = e

    # Assert
    assert error.error_code == ApiKeyErrorCode.NOT_FOUND


def test_deny_key_already_denied(module_client, function_empty_db):
    # Arrange
    error = None
    key1 = None
    create_fake_key(function_empty_db.session, denied=True)

    # Act
    try:
        key1 = deny_key(FAKE_APIKEY, True, function_empty_db.session)
    except ApiKeyError as e:
        error = e

    # Assert
    assert error.error_code == ApiKeyErrorCode.ALREADY_DENIED
    assert key1 is None


def test_deny_key_not_denied(module_client, function_empty_db):
    # Arrange
    error = None
    key1 = None
    create_fake_key(function_empty_db.session)

    # Act
    try:
        key1 = deny_key(FAKE_APIKEY, False, function_empty_db.session)
    except ApiKeyError as e:
        error = e

    # Assert
    assert error.error_code == ApiKeyErrorCode.NOT_DENIED
    assert key1 is None


def test_deny_key_set_denied_on(module_client, function_empty_db):
    # Arrange
    key = create_fake_key(function_empty_db.session)

    # Act
    key1 = deny_key(FAKE_APIKEY, True, function_empty_db.session)

    # Assert
    assert key.denied
    assert key == key1


def test_deny_key_set_denied_off(module_client, function_empty_db):
    # Arrange
    key = create_fake_key(function_empty_db.session, denied=True)

    # Act
    key1 = deny_key(FAKE_APIKEY, False, function_empty_db.session)

    # Assert
    assert not key.denied
    assert key == key1


def test_rotate_key(module_client, function_empty_db):
    # Arrange
    key = create_fake_key(function_empty_db.session)
    function_empty_db.session.add(key)
    function_empty_db.session.commit()

    # Act
    rotate_key(key, function_empty_db.session)

    # Assert
    assert key.apikey != FAKE_APIKEY
