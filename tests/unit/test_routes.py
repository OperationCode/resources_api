import pytest
from tests import conftest
from app.models import Resource, Language, Category
from configs import PaginatorConfig
from app.cli import import_resources


##########################################
## Tests
##########################################

# TODO: We need negative unit tests (what happens when bad data is sent)

def test_getters(app, session, db):
    # Importing the data takes a rather long time, so import it once
    # here for all the getters that require pages of resources
    import_resources(db)
    client = app.test_client()

    # Actually conduct all the tests in helper functions
    # get_resources_test(app, session, db, client)
    # paginator_test(app, session, db, client)
    # filters_test(app, session, db, client)
    # languages_test(app, session, db, client)
    # categories_test(app, session, db, client)


def test_create_resource(app, session, db):
    client = app.test_client()

    response = create_resource(client)
    assert (response.status_code == 200)
    assert (isinstance(response.json['data'].get('id'), int))
    assert (response.json['data'].get('name') == "Some Name")


def test_update_resource(app, session, db):
    client = app.test_client()

    response = create_resource(client)

    id = response.json['data'].get('id')
    assert (isinstance(id, int))

    response = client.put(f"/api/v1/resources/{id}", json={
        "name": "New name"
    })

    assert (response.status_code == 200)
    assert (response.json['data'].get('name') == "New name")


##########################################
## Helpers
##########################################

def test_get_resources(app, session, db):
    import_resources(db)
    client = app.test_client()

    response = client.get('api/v1/resources')

    # Status should be OK
    assert (response.status_code == 200)

    resources = response.json

    # Default page size shouold be specified in PaginatorConfig
    assert (len(resources['data']) == PaginatorConfig.per_page)

    for resource in resources['data']:
        assert (isinstance(resource.get('name'), str))
        assert (resource.get('name') != "")
        assert (isinstance(resource.get('url'), str))
        assert (resource.get('url') != "")
        assert (isinstance(resource.get('category'), str))
        assert (resource.get('category') != "")
        assert (type(resource.get('languages')) is list)


def test_get_single_resource(app, session, db):
    import_resources(db)
    client = app.test_client()

    response = client.get('api/v1/resources/5')

    # Status should be OK
    assert (response.status_code == 200)

    resource = response.json['data']
    print(resource)
    assert (isinstance(resource.get('name'), str))
    assert (resource.get('name') != "")
    assert (isinstance(resource.get('url'), str))
    assert (resource.get('url') != "")
    assert (isinstance(resource.get('category'), str))
    assert (resource.get('category') != "")
    assert (type(resource.get('languages')) is list)

    assert (resource.get('id') == 5)


def test_paginator(app, session, db):
    import_resources(db)
    client = app.test_client()

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
    assert (len(response.json['data']) == 0)


def test_filters(app, session, db):
    import_resources(db)
    client = app.test_client()

    # Filter by language
    response = client.get('api/v1/resources?language=python')

    for resource in response.json['data']:
        assert (type(resource.get('languages')) is list)
        assert ('Python' in resource.get('languages'))

    # Filter by category
    response = client.get('api/v1/resources?category=Back%20End%20Dev')

    for resource in response.json['data']:
        assert (resource.get('category') == "Back End Dev")

    # TODO: Filter by updated_after
    # (Need to figure out how to manually set last_updated and created_at)


def test_languages(app, session, db):
    import_resources(db)
    client = app.test_client()

    response = client.get('api/v1/languages')
    for language in response.json['data']:
        assert (isinstance(language.get('id'), int))
        assert (isinstance(language.get('name'), str))
        assert (len(language.get('name')) > 0)


def test_categories(app, session, db):
    import_resources(db)
    client = app.test_client()

    response = client.get('api/v1/categories')

    for category in response.json['data']:
        assert (isinstance(category.get('id'), int))
        assert (isinstance(category.get('name'), str))
        assert (len(category.get('name')) > 0)


def create_resource(client):
    return client.post('/api/v1/resources', json={
        "name": "Some Name",
        "url": "http://example.org/",
        "category": "New Category",
        "languages": ["Python", "New Language"],
        "paid": False,
        "notes": "Some notes"
    })
