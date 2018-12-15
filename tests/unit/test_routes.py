import pytest
from tests import conftest
from app.models import Resource, Language, Category


def test_does_nothing():
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, hashed_password, authenticated, and role fields are defined correctly
    """
    assert(1 == 1)

def test_get_resources(app, client):
    resources = client.get('api/v1/resources')
    assert(resources.status_code == 200)
