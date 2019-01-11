import requests


def authenticate(func):

    def wrapper(*args, **kwargs):
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
