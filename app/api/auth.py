import requests
from flask import request
from app.models import Key
from app.utils import standardize_response, setup_logger

create_logger = setup_logger('create_auth_logger', 'log/create_auth.log')
update_logger = setup_logger('update_auth_logger', 'log/update_auth.log')


def authenticate(func):
    def wrapper(*args, **kwargs):
        apikey = request.headers.get('x-apikey')
        key = Key.query.filter_by(apikey=apikey).first()

        if not key:
            errors = [{"code": "not-authorized"}]
            return standardize_response(None, errors, "not authorized", 401)

        log_request(request, key)

        return func(*args, **kwargs)
    return wrapper


def is_user_oc_member(email, password):
    response = requests.post('https://api.operationcode.org/api/v1/sessions', json=dict(
            user=dict(email=email,
                      password=password
                      )
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
