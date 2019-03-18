import pytest
from tests import conftest
from app.models import Resource, Language, Category
from configs import PaginatorConfig
from app.cli import import_resources


##########################################
## Test Routes
##########################################


# TODO: We need negative unit tests (what happens when bad data is sent)
def test_get_resources(module_client, module_db):
    client = module_client

    response = client.get('api/v1/resources')

    # Status should be OK
    assert (response.status_code == 200)

    resources = response.json

    # Default page size should be specified in PaginatorConfig
    assert (len(resources['data']) == PaginatorConfig.per_page)

    for resource in resources['data']:
        assert (isinstance(resource.get('name'), str))
        assert (resource.get('name'))
        assert (isinstance(resource.get('url'), str))
        assert (resource.get('url'))
        assert (isinstance(resource.get('category'), str))
        assert (resource.get('category'))
        assert (isinstance(resource.get('languages'), list))


def test_get_single_resource(module_client, module_db):
    client = module_client

    response = client.get('api/v1/resources/5')

    # Status should be OK
    assert (response.status_code == 200)

    resource = response.json['data']
    assert (isinstance(resource.get('name'), str))
    assert (resource.get('name'))
    assert (isinstance(resource.get('url'), str))
    assert (resource.get('url'))
    assert (isinstance(resource.get('category'), str))
    assert (resource.get('category'))
    assert (isinstance(resource.get('languages'), list))

    assert (resource.get('id') == 5)


def test_get_favicon(module_client):
    response = module_client.get("favicon.ico")
    assert (response.status_code == 200)


def test_paginator(module_client, module_db):
    client = module_client

    # Test page size
    response = client.get('api/v1/resources?page_size=1')
    assert (len(response.json['data']) == 1)
    response = client.get('api/v1/resources?page_size=5')
    assert (len(response.json['data']) == 5)
    response = client.get('api/v1/resources?page_size=10')
    assert (len(response.json['data']) == 10)
    response = client.get('api/v1/resources?page_size=100')
    assert (len(response.json['data']) == 100)

    # Test pages different and sequential
    first_page_resource = response.json['data'][0]
    assert (first_page_resource.get('id') == 1)
    response = client.get('api/v1/resources?page_size=100&page=2')
    second_page_resource = response.json['data'][0]
    assert (second_page_resource.get('id') == 101)
    response = client.get('api/v1/resources?page_size=100&page=3')
    third_page_resource = response.json['data'][0]
    assert (third_page_resource.get('id') == 201)

    # Test bigger than max page size
    too_long = PaginatorConfig.max_page_size + 1
    response = client.get(f"api/v1/resources?page_size={too_long}")
    assert (len(response.json['data']) == PaginatorConfig.max_page_size)

    # Test farther than last page
    too_far = 99999999
    response = client.get(f"api/v1/resources?page_size=100&page={too_far}")
    assert (not response.json['data'])


def test_filters(module_client, module_db):
    client = module_client

    # Filter by language
    response = client.get('api/v1/resources?language=python')

    for resource in response.json['data']:
        assert (isinstance(resource.get('languages'), list))
        assert ('Python' in resource.get('languages'))

    # Filter by category
    response = client.get('api/v1/resources?category=Back%20End%20Dev')

    for resource in response.json['data']:
        assert (resource.get('category') == "Back End Dev")

    # TODO: Filter by updated_after
    # (Need to figure out how to manually set last_updated and created_at)


def test_languages(module_client, module_db):
    client = module_client

    response = client.get('api/v1/languages')
    for language in response.json['data']:
        assert (isinstance(language.get('id'), int))
        assert (isinstance(language.get('name'), str))
        assert (language.get('name'))


def test_categories(module_client, module_db):
    client = module_client

    response = client.get('api/v1/categories')

    for category in response.json['data']:
        assert (isinstance(category.get('id'), int))
        assert (isinstance(category.get('name'), str))
        assert (category.get('name'))


def test_update_votes(module_client, module_db):
    client = module_client
    vote_direction = 'upvote'
    id = 1

    # Check voting on a valid resource
    data = client.get(f"api/v1/resources/{id}").json['data']
    response = client.put(f"/api/v1/resources/{id}/{vote_direction}", follow_redirects=True)
    initial_votes = data.get(f"{vote_direction}s")

    assert (response.status_code == 200)
    assert (response.json['data'].get(f"{vote_direction}s") == initial_votes + 1)

    vote_direction = 'downvote'
    response = client.put(f"/api/v1/resources/{id}/{vote_direction}", follow_redirects=True)
    assert (response.status_code == 200)
    assert (response.json['data'].get(f"{vote_direction}s") == initial_votes + 1)

    # Check voting on an invalid resource
    id = 'waffles'
    response = client.put(f"/api/v1/resources/{id}/{vote_direction}", follow_redirects=True)
    assert (response.status_code == 404)
    assert (response.json.get('errors')[0].get('code') == "not-found")

    # Check voting on a resource that doesn't exist
    too_high = 99999999
    response = client.put(f"/api/v1/resources/{too_high}/{vote_direction}", follow_redirects=True)
    assert (response.status_code == 404)
    assert (response.json.get('errors')[0].get('code') == "not-found")


##########################################
## Authenticated Routes
##########################################


def test_apikey_commit_error(module_client, module_db, fake_auth_from_oc, fake_commit_error):
    client = module_client

    response = client.post('api/v1/apikey', json = dict(
        email="test@example.org",
        password="supersecurepassword"
    ))

    assert (response.status_code == 500)


def test_get_api_key(module_client, module_db, fake_auth_from_oc):
    client = module_client

    response = client.post('api/v1/apikey', json = dict(
        email="test@example.org",
        password="supersecurepassword"
    ))

    assert (response.status_code == 200)
    assert (response.json['data'].get('email') == "test@example.org")
    assert (isinstance(response.json['data'].get('apikey'), str))


def test_get_api_key(module_client, module_db, fake_invalid_auth_from_oc):
    client = module_client

    response = client.post('api/v1/apikey',
        follow_redirects=True,
        json = dict(
            email="test@example.org",
            password="invalidpassword"
    ))

    assert (response.status_code == 401)


def test_create_resource(module_client, module_db, fake_auth_from_oc):
    client = module_client

    # Happy Path
    apikey = get_api_key(client)
    response = create_resource(client, apikey)
    assert (response.status_code == 200)
    assert (isinstance(response.json['data'].get('id'), int))
    assert (response.json['data'].get('name') == "Some Name")

    # Invalid API Key Path
    response = create_resource(client, "invalidapikey")
    assert (response.status_code == 401)


def test_update_resource(module_client, module_db, fake_auth_from_oc):
    client = module_client

    # Happy Path
    apikey = get_api_key(client)

    response = client.put("/api/v1/resources/1",
        json = dict(
            name="New name",
            languages=["New language"],
            category="New Category",
            url="https://new.url",
            paid=False,
            notes="New notes"
        ),
        headers = {'x-apikey': apikey}
    )

    assert (response.status_code == 200)
    assert (response.json['data'].get('name') == "New name")

    # Resource not found
    response = client.put("/api/v1/resources/0",
        json = dict(name="New name"),
        headers = {'x-apikey': apikey},
        follow_redirects = True
    )
    assert (response.status_code == 404)


def test_commit_errors(module_client, module_db, fake_auth_from_oc, fake_commit_error):
    client = module_client
    apikey = get_api_key(client)

    response = client.put("/api/v1/resources/1",
        json = dict(name="New name"),
        headers = {'x-apikey': apikey}
    )
    assert (response.status_code == 500)

    response = create_resource(client, apikey)
    assert (response.status_code == 500)


def test_key_query_error(module_client, module_db, fake_auth_from_oc, fake_key_query_error):
    client = module_client
    response = client.post('api/v1/apikey', json = dict(
        email="test@example.org",
        password="supersecurepassword"
    ))
    assert (response.status_code == 500)

def test_internal_server_error_handler(module_client, module_db, fake_items_error):
    client = module_client

    response = client.get('api/v1/resources')
    assert (response.status_code == 500)
    assert (response.json['errors'][0].get("code") == "server-error")

    response = client.get('api/v1/languages')
    assert (response.status_code == 500)
    assert (response.json['errors'][0].get("code") == "server-error")

    response = client.get('api/v1/categories')
    assert (response.status_code == 500)
    assert (response.json['errors'][0].get("code") == "server-error")


##########################################
## Other Routes
##########################################


# This method must come last if using the persistent client and db
def test_rate_limit(module_client, module_db):
    client = module_client

    for _ in range(50):
        client.get('api/v1/resources')

    # Response should be a failure on request 51
    response = client.get('api/v1/resources')
    assert(response.status_code == 429)
    assert (isinstance(response.json.get('errors'), list))
    assert(response.json.get('errors')[0].get('code') == "rate-limit-exceeded")


##########################################
## Helpers
##########################################
def create_resource(client, apikey):
    return client.post('/api/v1/resources',
        json = dict(
            name="Some Name",
            url="http://example.org/",
            category="New Category",
            languages=["Python", "New Language"],
            paid=False,
            notes="Some notes"
        ),
        headers = {'x-apikey': apikey}
    )

def get_api_key(client):
   response = client.post('api/v1/apikey', json = dict(
        email="test@example.org",
        password="supersecurepassword"
   ))

   return response.json['data'].get('apikey')
