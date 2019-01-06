import pytest
from tests import conftest
from app.models import Resource, Language, Category
from configs import PaginatorConfig
from app.cli import import_resources


##########################################
## Test Routes
##########################################


def test_create_resource(session_app, function_session, session_db):
    client = session_app.test_client()

    response = create_resource(client)
    assert (response.status_code == 200)
    assert (isinstance(response.json['data'].get('id'), int))
    assert (response.json['data'].get('name') == "Some Name")


def test_update_resource(session_app, function_session, session_db):
    client = session_app.test_client()

    response = create_resource(client)

    id = response.json['data'].get('id')
    assert (isinstance(id, int))

    response = client.put(f"/api/v1/resources/{id}", json={
        "name": "New name"
    })

    assert (response.status_code == 200)
    assert (response.json['data'].get('name') == "New name")



##########################################
## Persistent data routes
##########################################


##########################################
## Helpers
##########################################
def create_resource(client):
    return client.post('/api/v1/resources', json={
        "name": "Some Name",
        "url": "http://example.org/",
        "category": "New Category",
        "languages": ["Python", "New Language"],
        "paid": False,
        "notes": "Some notes"
    })
