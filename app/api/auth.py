import uuid
import os
from enum import Enum
import functools

import requests
from app import db
from app.models import Key
from app.utils import setup_logger, standardize_response
from flask import g, request

from jwt import decode, InvalidSignatureError, ExpiredSignatureError

PUBLIC_KEY = os.environ.get('JWT_PUBLIC_KEY', open(".dev/dev-jwt-key.pub").read())

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
    ALREADY_DENIED = 2
    NOT_DENIED = 3


def find_key_by_apikey_or_email(apikey_or_email):
    key = Key.query.filter_by(apikey=apikey_or_email).first()
    if key:
        return key
    return Key.query.filter_by(email=apikey_or_email).first()


def deny_key(apikey_or_email, denied, session):
    key = find_key_by_apikey_or_email(apikey_or_email)
    if not key:
        raise ApiKeyError('Could not find that apikey or email.',
                          ApiKeyErrorCode.NOT_FOUND)

    if key.denied == denied:
        raise ApiKeyError(
            ('Already' if denied else 'Not') + ' denied',
            ApiKeyErrorCode.ALREADY_DENIED if denied
            else ApiKeyErrorCode.NOT_DENIED
        )

    key.denied = denied

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


def jwt_to_key():
    auth_header = request.headers.get("authorization")
    if not auth_header:
        return None
    auth_parts = auth_header.split(" ")
    if len(auth_parts) != 2:
        return None
    _, token = auth_parts
    try:
        decoded_token = decode(
            token, PUBLIC_KEY, algorithms="RS256"
        )
        request.decoded_token = decoded_token
    except InvalidSignatureError:
        return None
    except ExpiredSignatureError:
        return None
    if 'exp' not in decoded_token:
        return None
    return get_api_key_from_authenticated_email(decoded_token['email'])


# NOTE: this function assumes the email has already been authenticated
def get_api_key_from_authenticated_email(email):
    apikey = Key.query.filter_by(email=email).first()

    if apikey and apikey.denied:
        return None

    if not apikey:
        apikey = create_new_apikey(email, db.session)
        if not apikey:
            raise Exception
    return apikey


def authenticate(func=None, allow_no_auth_key=False):
    if not func:
        return functools.partial(authenticate, allow_no_auth_key=allow_no_auth_key)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        apikey = request.headers.get('x-apikey')
        try:
            filters = {'apikey': apikey, 'denied': False}
            key = Key.query.filter_by(**filters).first() if apikey else jwt_to_key()
        except Exception:
            return standardize_response(status_code=500)

        if not key and not allow_no_auth_key:
            return standardize_response(status_code=401)

        if key:
            log_request(request, key)

        g.auth_key = key

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
    payload = request.get_json(silent=True)
    logger = create_logger if method == "POST" else update_logger
    logger.info(f"User: {user} Route: {path} Payload: {payload}")
