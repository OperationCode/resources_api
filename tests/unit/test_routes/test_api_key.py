from app.api.auth import blacklist_key
from .helpers import get_api_key, assert_correct_response
from tests.utils import apikey_commit


def test_get_api_key(module_client, module_db, fake_auth_from_oc):

    response = apikey_commit(module_client, "test@example.org", "supersecurepassword")

    assert (response.status_code == 200)
    assert (response.json['credentials'].get('email') == "test@example.org")
    assert (isinstance(response.json['credentials'].get('apikey'), str))


def test_rotate_api_key(module_client, module_db, fake_auth_from_oc):
    client = module_client

    apikey = get_api_key(client)
    response = client.post('api/v1/apikey/rotate', headers={'x-apikey': apikey})

    assert (response.status_code == 200)
    assert (isinstance(response.json['credentials'].get('email'), str))
    assert (isinstance(response.json['credentials'].get('apikey'), str))
    assert (response.json['credentials'].get('apikey') != apikey)


def test_apikey_commit_error(
        module_client, module_db, fake_auth_from_oc, fake_commit_error):

    response = apikey_commit(module_client, "test@example.com", "password")
    assert_correct_response(response, 500)


def test_get_api_key_bad_password(module_client, module_db, fake_invalid_auth_from_oc):

    response = apikey_commit(module_client, "test@example.org", "invalidpassword",
                             follow_redirects=True)

    assert_correct_response(response, 401)


def test_get_api_key_blacklisted(module_client, module_db, fake_auth_from_oc):
    client = module_client

    apikey = get_api_key(client)
    blacklist_key(apikey, True, module_db.session)

    try:
        response = apikey_commit(client, "test@example.org", "supersecurepassword",
                                 follow_redirects=True)
        assert_correct_response(response, 401)
    finally:
        blacklist_key(apikey, False, module_db.session)


def test_rotate_api_key_unauthorized(module_client, module_db):
    client = module_client

    response = client.post('api/v1/apikey/rotate')

    assert_correct_response(response, 401)


def test_key_query_error(
        module_client, module_db, fake_auth_from_oc, fake_key_query_error):
    response = apikey_commit(module_client, "test@example.com", "supersecurepassword")
    assert_correct_response(response, 500)
