from app.api.auth import blacklist_key
from .helpers import get_api_key


def test_apikey_commit_error(
        module_client, module_db, fake_auth_from_oc, fake_commit_error):
    client = module_client

    response = client.post('api/v1/apikey', json=dict(
        email="test@example.org",
        password="supersecurepassword"
    ))

    assert (response.status_code == 500)


def test_get_api_key(module_client, module_db, fake_auth_from_oc):
    client = module_client

    response = client.post('api/v1/apikey', json=dict(
        email="test@example.org",
        password="supersecurepassword"
    ))

    assert (response.status_code == 200)
    assert (response.json['data'].get('email') == "test@example.org")
    assert (isinstance(response.json['data'].get('apikey'), str))


def test_get_api_key_bad_password(module_client, module_db, fake_invalid_auth_from_oc):
    client = module_client

    response = client.post('api/v1/apikey',
                           follow_redirects=True,
                           json=dict(
                               email="test@example.org",
                               password="invalidpassword"
                           ))

    assert (response.status_code == 401)


def test_get_api_key_blacklisted(module_client, module_db, fake_auth_from_oc):
    client = module_client

    apikey = get_api_key(client)
    blacklist_key(apikey, True, module_db.session)

    try:
        response = client.post(
            'api/v1/apikey',
            follow_redirects=True,
            json=dict(
                email="test@example.org",
                password="supersecurepassword"
            )
        )
        assert (response.status_code == 401)
    finally:
        blacklist_key(apikey, False, module_db.session)


def test_rotate_api_key_unauthorized(module_client, module_db):
    client = module_client

    response = client.post('api/v1/apikey/rotate')

    assert (response.status_code == 401)


def test_rotate_api_key(module_client, module_db, fake_auth_from_oc):
    client = module_client

    apikey = get_api_key(client)
    response = client.post('api/v1/apikey/rotate', headers={'x-apikey': apikey})

    assert (response.status_code == 200)
    assert (isinstance(response.json['data'].get('email'), str))
    assert (isinstance(response.json['data'].get('apikey'), str))
    assert (response.json['data'].get('apikey') != apikey)


def test_key_query_error(
        module_client, module_db, fake_auth_from_oc, fake_key_query_error):
    client = module_client
    response = client.post('api/v1/apikey', json=dict(
        email="test@example.org",
        password="supersecurepassword"
    ))
    assert (response.status_code == 500)
