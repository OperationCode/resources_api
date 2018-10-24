import pytest
from src.app import Resource, Language, Category


def test_does_nothing():
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, hashed_password, authenticated, and role fields are defined correctly
    """
    assert(1 == 1)
