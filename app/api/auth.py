import requests
from flask import request
from app.models import Key
from app.utils import standardize_response


def authenticate(func):
    def wrapper(*args, **kwargs):
        apikey = request.headers.get('x-apikey')
        if not Key.query.filter_by(apikey=apikey).first():
            errors = [{"code": "not-authorized"}]
            return standardize_response(None, errors, "not authorized", 401)
        return func(*args, **kwargs)
    return wrapper


def check_user_with_oc(json):
    response = requests.post('https://api.operationcode.org/api/v1/sessions', json={
        "user": {
            "email": json.get('email'),
            "password": json.get('password')
        }
    })

    return bool(response.json().get('token'))
