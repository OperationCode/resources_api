from datetime import datetime

from app.models import Category, Key, Language, Resource, VoteInformation


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
    assert (resource.__repr__() == "<Resource \n"
            "\tName: name\n"
            "\tLanguages: [<Language language>]\n"
            "\tCategory: <Category Category>\n"
            "\tURL: https://resource.url\n>")

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
    assert (category.__repr__() == "<Category Category>")
    assert (category != 1)
    assert (category == category)


def test_language():
    language = Language(name="Language")
    assert (language.__hash__() == hash('Language'))
    assert (language.__repr__() == "<Language Language>")
    assert (language != 1)
    assert (language == language)


def test_key():
    key = Key(email="test@example.org", apikey="1234abcd")
    assert (key.__hash__() == hash('1234abcd'))
    assert (key.__repr__() == "<Key email=test@example.org apikey=1234abcd>")
    assert (key != 1)
    assert (key == key)
    time = datetime.now()
    key.last_updated = time
    assert (key.serialize == {'apikey': '1234abcd',
                              'created_at': '',
                              'email': 'test@example.org',
                              'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")
                              })


def test_key_denied():
    key = Key(email="test@example.org", apikey="1234abcd", denied=True)
    assert (
        key.__repr__() == "<Key email=test@example.org apikey=1234abcd DENIED>"
    )
    assert (key != 1)
    assert (key == key)
    time = datetime.now()
    key.last_updated = time
    assert (key.serialize == {'apikey': '1234abcd',
                              'created_at': '',
                              'email': 'test@example.org',
                              'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")
                              })


def test_vote_information():
    test_apikey = '1234abcd'
    test_id = 1
    test_direction = 'upvote'

    resource = Resource(
        id=test_id,
        name='name',
        url='https://resource.url',
        category=Category(name='Category'),
        languages=[Language(name='language')],
        paid=False,
        notes='Some notes'
    )
    key = Key(email="test@example.org", apikey=test_apikey)

    vote_info = VoteInformation(
        voter_apikey=key.apikey,
        resource_id=resource.id,
        current_direction=test_direction
    )
    vote_info.voter = key
    resource.voters.append(vote_info)

    assert(vote_info.voter_apikey == test_apikey)
    assert(vote_info.resource_id == test_id)
    assert(vote_info.current_direction == test_direction)
    assert(vote_info.voter == key)
    assert(vote_info.resource == resource)
