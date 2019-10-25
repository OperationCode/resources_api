from datetime import datetime

import pytest
from app.models import Category, Key, Language, Resource
from tests import conftest


def test_resource():
    resource = Resource(
        name='name',
        url='https://resource.url',
        category=Category(name='Category'),
        languages=[Language(name='language')],
        paid=False,
        notes='Some notes'
    )

    assert (resource.key() == 'https://resource.url')
    assert (resource.__hash__() == hash('https://resource.url'))
    assert (resource.__repr__() == f"<Resource \n"
            f"\tName: name\n"
            f"\tLanguages: [<Language language>]\n"
            f"\tCategory: <Category Category>\n"
            f"\tURL: https://resource.url\n>")

    assert (resource.serialize == {
        'id': None,
        'name': 'name',
        'url': 'https://resource.url',
        'category': 'Category',
        'languages': ['language'],
        'paid': False,
        'notes': 'Some notes',
        'upvotes': None,
        'downvotes': None,
        'times_clicked': None,
        'created_at': '',
        'last_updated': ''
    })

    # Test equality
    resource_copy = resource
    assert (resource == resource_copy)

    not_copy = Resource(name='different name')
    assert (resource != not_copy)
    not_copy.name = 'name'
    not_copy.url = 'https://notresource.url'
    assert (resource != not_copy)
    not_copy.url = 'https://resource.url'
    assert (resource != not_copy)
    not_copy.paid = True
    assert (resource != not_copy)
    not_copy.paid = False
    not_copy.notes = 'Some other notes'
    assert (resource != not_copy)
    not_copy.notes = 'Some notes'
    not_copy.category = 'Different Category'
    assert (resource != not_copy)
    not_copy.category = Category(name='Category')
    not_copy.languages = ["different language"]
    assert (resource != not_copy)
    not_copy.languages = [Language(name='language')]
    assert (resource == not_copy)
    assert (resource != 1)


def test_category():
    category = Category(name="Category")
    assert (category.__hash__() == hash('Category'))
    assert (category.__repr__() == f"<Category Category>")
    assert (category != 1)
    assert (category == category)


def test_language():
    language = Language(name="Language")
    assert (language.__hash__() == hash('Language'))
    assert (language.__repr__() == f"<Language Language>")
    assert (language != 1)
    assert (language == language)


def test_key():
    key = Key(email="test@example.org", apikey="1234abcd")
    assert (key.__hash__() == hash('1234abcd'))
    assert (key.__repr__() == f"<Key email=test@example.org apikey=1234abcd>")
    assert (key != 1)
    assert (key == key)
    time = datetime.now()
    key.last_updated = time
    assert (key.serialize == {'apikey': '1234abcd',
                              'created_at': '',
                              'email': 'test@example.org',
                              'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")
                              })


def test_key_blacklisted():
    key = Key(email="test@example.org", apikey="1234abcd", blacklisted=True)
    assert (key.__repr__() == f"<Key email=test@example.org apikey=1234abcd BLACKLISTED>")
    assert (key != 1)
    assert (key == key)
    time = datetime.now()
    key.last_updated = time
    assert (key.serialize == {'apikey': '1234abcd',
                              'created_at': '',
                              'email': 'test@example.org',
                              'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")
                              })
