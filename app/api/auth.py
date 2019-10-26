import uuid
from enum import Enum

import requests
from app.models import Key
from app.utils import setup_logger, standardize_response
from flask import request

auth_logger = setup_logger('auth_logger')
create_logger = setup_logger('create_auth_logger')
update_logger = setup_logger('update_auth_logger')


class ApiKeyError(Exception):
    def __init__(self, message, error_code):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ApiKeyErrorCode(Enum):
    NOT_FOUND = 1
    ALREADY_BLACKLISTED = 2
    NOT_BLACKLISTED = 3


def find_key_by_apikey_or_email(apikey_or_email):
    key = Key.query.filter_by(apikey=apikey_or_email).first()
    if key:
        return key
    return Key.query.filter_by(email=apikey_or_email).first()


def blacklist_key(apikey_or_email, blacklisted, session):
    key = find_key_by_apikey_or_email(apikey_or_email)
    if not key:
        raise ApiKeyError('Could not find that apikey or email.',
                          ApiKeyErrorCode.NOT_FOUND)

    if key.blacklisted == blacklisted:
        raise ApiKeyError(
            ('Already' if blacklisted else 'Not') + ' blacklisted',
            ApiKeyErrorCode.ALREADY_BLACKLISTED if blacklisted
            else ApiKeyErrorCode.NOT_BLACKLISTED
        )

    key.blacklisted = blacklisted

    session.commit()

    return key


def get_new_key_value():
    return uuid.uuid4().hex


def create_new_apikey(email, session):
    # TODO: we should put this in a while loop in the extremely unlikely chance
    # there is a collision of UUIDs in the database. It is assumed at this point
    # in the flow that the DB was already checked for this email address, and
    # no key exists yet.
    new_key = Key(
        apikey=get_new_key_value(),
        email=email
    )

    try:
        session.add(new_key)
        session.commit()

        return new_key
    except Exception as e:
        auth_logger.exception(e)
        return None


def rotate_key(key, session):
    key.apikey = get_new_key_value()
    try:
        session.commit()
        return key
    except Exception as e:
        auth_logger.exception(e)
        return None


def authenticate(func):
    def wrapper(*args, **kwargs):
        apikey = request.headers.get('x-apikey')
        key = Key.query.filter_by(apikey=apikey, blacklisted=False).first()

        if not key:
            return standardize_response(status_code=401)

        log_request(request, key)

        return func(*args, **kwargs)
    return wrapper


def is_user_oc_member(email, password):
    response = requests.post(
        'https://api.operationcode.org/auth/login/',
        json=dict(
            email=email,
            password=password
        )
    )

    return bool(response.json().get('token'))


def log_request(request, key):
    method = request.method
    path = request.path
    user = key.email
    payload = request.json
    logger = create_logger if method == "POST" else update_logger
    logger.info(f"User: {user} Route: {path} Payload: {payload}")
