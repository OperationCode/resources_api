from datetime import datetime, timedelta
from os import environ

from app.api.auth import blacklist_key
from app.utils import get_error_code_from_status, msg_map, random_string
from app.api.validations import MISSING_BODY, MISSING_PARAMS, INVALID_PARAMS
from configs import PaginatorConfig

##########################################
# Test Routes
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
    assert (resources['number_of_pages'] is not None)

    ua = datetime.now() + timedelta(days=-7)
    uaString = ua.strftime('%m-%d-%Y')
    response = client.get(f"/api/v1/resources?updated_after={uaString}")
    assert (response.status_code == 200)

    # Test trying to get a page of results that doesn't exist
    too_far = 99999999
    response = client.get(
        f"api/v1/resources?page_size=100&page={too_far}", follow_redirects=True)
    assert (response.status_code == 404)
    assert (
        isinstance(response.json.get('errors').get(
            get_error_code_from_status(response.status_code)), dict))
    assert (
        isinstance(response.json.get('errors').get(
            get_error_code_from_status(response.status_code)).get('message'), str))


def test_get_resources_post_date_failure(module_client):
    client = module_client
    # If updated_after date is after today, then should return a 422
    ua = datetime.now() + timedelta(days=1)
    uaString = ua.strftime('%m-%d-%Y')
    response = client.get(f"/api/v1/resources?updated_after={uaString}")
    assert (response.status_code == 422)
    assert (isinstance(response.json.get('errors').get(
        get_error_code_from_status(response.status_code)), dict))
    assert (isinstance(response.json.get('errors').get(
        get_error_code_from_status(response.status_code)).get('message'), str))


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


def test_single_resource_out_of_bounds(module_client, module_db):
    client = module_client

    too_low = 0
    too_high = 9999
    response = client.get(f"api/v1/resources/{too_low}", follow_redirects=True)

    assert (response.status_code == 404)

    response = client.get(f"api/v1/resources/{too_high}", follow_redirects=True)

    assert (response.status_code == 404)


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
    assert (response.json['records_per_page'] == PaginatorConfig.max_page_size)

    # Test pagination details are included
    page_size = 51
    response = client.get(f"api/v1/resources?page_size={page_size}").json
    assert (response['number_of_pages'] is not None)
    assert (response['records_per_page'] == page_size)
    assert (response['page'] == 1)
    assert (response['total_count'] is not None)
    assert (response['has_next'] is not None)
    assert (response['has_prev'] is not None)


def test_paid_filter(module_client, module_db):
    client = module_client

    total_resources = client.get('api/v1/resources').json['total_count']

    # Filter by paid
    response = client.get('api/v1/resources?paid=false')

    total_free_resources = response.json['total_count']

    assert all([not res.get('paid') for res in response.json['data']])

    response = client.get('api/v1/resources?paid=true')

    total_paid_resources = response.json['total_count']

    assert all([res.get('paid') for res in response.json['data']])

    # Check that the number of resources appear correct
    assert (total_paid_resources > 0)
    assert (total_free_resources > 0)
    assert (total_resources == total_free_resources + total_paid_resources)


def test_paid_filter_works_with_uppercase_parameter(module_client, module_db):
    client = module_client

    response = client.get('api/v1/resources?paid=TRUE')
    assert all([res.get('paid') for res in response.json['data']])

    response = client.get('api/v1/resources?paid=FALSE')
    assert all([not res.get('paid') for res in response.json['data']])


def test_paid_filter_defaults_all_when_invalid_paid_parameter(module_client, module_db):
    client = module_client

    response = client.get('api/v1/resources?paid=na93ns8i1ns')

    assert (True in [res.get('paid') for res in response.json['data']])
    assert (False in [res.get('paid') for res in response.json['data']])


def test_filters(module_client, module_db):
    client = module_client

    # Filter by one language
    response = client.get('api/v1/resources?languages=python')

    for resource in response.json['data']:
        assert (isinstance(resource.get('languages'), list))
        assert ('Python' in resource.get('languages'))

    # Filter by multiple languages
    response = client.get('api/v1/resources?languages=python&languages=javascript')

    for resource in response.json['data']:
        assert (isinstance(resource.get('languages'), list))
        assert (
            ('Python' in resource.get('languages')) or
            ('JavaScript' in resource.get('languages'))
        )

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
    assert (response.json['number_of_pages'] is not None)

    # Test trying to get a page of results that doesn't exist
    too_far = 99999999
    response = client.get(
        f"api/v1/languages?page_size=100&page={too_far}", follow_redirects=True)
    assert (response.status_code == 404)
    assert (isinstance(response.json.get('errors').get(
        get_error_code_from_status(response.status_code)), dict))
    assert (isinstance(response.json.get('errors').get(
        get_error_code_from_status(response.status_code)).get('message'), str))


def test_get_single_language(module_client, module_db):
    client = module_client

    response = client.get('api/v1/languages/3')

    # Status should be OK
    assert (response.status_code == 200)

    language = response.json['data']
    assert (isinstance(language.get('name'), str))
    assert (language.get('name'))

    assert (language.get('id') == 3)


def test_single_language_out_of_bounds(module_client, module_db):
    client = module_client

    too_low = 0
    too_high = 9999
    response = client.get(f"api/v1/languages/{too_low}", follow_redirects=True)

    assert (response.status_code == 404)

    response = client.get(f"api/v1/languages/{too_high}", follow_redirects=True)

    assert (response.status_code == 404)


def test_categories(module_client, module_db):
    client = module_client

    response = client.get('api/v1/categories')

    for category in response.json['data']:
        assert (isinstance(category.get('id'), int))
        assert (isinstance(category.get('name'), str))
        assert (category.get('name'))
    assert (response.json['number_of_pages'] is not None)

    # Test trying to get a page of results that doesn't exist
    too_far = 99999999
    response = client.get(
        f"api/v1/categories?page_size=100&page={too_far}", follow_redirects=True)
    assert (response.status_code == 404)
    assert (isinstance(response.json.get('errors').get(
        get_error_code_from_status(response.status_code)), dict))
    assert (isinstance(response.json.get('errors').get(
        get_error_code_from_status(response.status_code)).get('message'), str))


def test_get_single_category(module_client, module_db):
    client = module_client

    response = client.get('api/v1/categories/4')

    # Status should be OK
    assert (response.status_code == 200)

    category = response.json['data']
    assert (isinstance(category.get('name'), str))
    assert (category.get('id') == 4)


def test_get_single_category_out_of_bounds(module_client, module_db):
    client = module_client

    # Check GET request to invalid category id - too low
    too_low = 0
    response = client.get(f"api/v1/categories/{too_low}", follow_redirects=True)
    assert (response.status_code == 404)

    # Check GET request to invalid category id - too high
    too_high = 9999
    response = client.get(f"api/v1/categories/{too_high}", follow_redirects=True)
    assert (response.status_code == 404)

    # Check GET request to invalid category id - non integer
    string = 'waffles'
    response = client.get(f"api/v1/categories/{string}", follow_redirects=True)
    assert (response.status_code == 404)

    empty_string = ' '
    response = client.get(f"api/v1/categories/{empty_string}", follow_redirects=True)
    assert (response.status_code == 404)

    symbol = '$'
    response = client.get(f"api/v1/categories/{symbol}", follow_redirects=True)
    assert (response.status_code == 404)


def test_update_votes(module_client, module_db, fake_algolia_save):
    client = module_client
    vote_direction = 'upvote'
    id = 1

    # Check voting on a valid resource
    data = client.get(f"api/v1/resources/{id}").json['data']
    response = client.put(
        f"/api/v1/resources/{id}/{vote_direction}", follow_redirects=True)
    initial_votes = data.get(f"{vote_direction}s")

    assert (response.status_code == 200)
    assert (response.json['data'].get(f"{vote_direction}s") == initial_votes + 1)

    vote_direction = 'downvote'
    response = client.put(
        f"/api/v1/resources/{id}/{vote_direction}", follow_redirects=True)
    assert (response.status_code == 200)
    assert (response.json['data'].get(f"{vote_direction}s") == initial_votes + 1)

    # Check voting on an invalid resource
    id = 'waffles'
    response = client.put(
        f"/api/v1/resources/{id}/{vote_direction}", follow_redirects=True)
    assert (response.status_code == 404)
    assert (isinstance(response.json.get('errors').get(
        get_error_code_from_status(response.status_code)), dict))
    assert (isinstance(response.json.get('errors').get(
        get_error_code_from_status(response.status_code)).get('message'), str))

    # Check voting on a resource that doesn't exist
    too_high = 99999999
    response = client.put(
        f"/api/v1/resources/{too_high}/{vote_direction}", follow_redirects=True)
    assert (response.status_code == 404)
    assert (isinstance(response.json.get('errors').get(
        get_error_code_from_status(response.status_code)), dict))
    assert (isinstance(response.json.get('errors').get(
        get_error_code_from_status(response.status_code)).get('message'), str))


def test_add_click(module_client, module_db):
    client = module_client

    # Check clicking on a valid resource
    id = 1
    data = client.get(f"api/v1/resources/{id}").json['data']
    response = client.put(f"/api/v1/resources/{id}/click", follow_redirects=True)
    initial_click_count = data.get(f"times_clicked")

    assert (response.status_code == 200)
    assert (response.json['data'].get(f"times_clicked") == initial_click_count + 1)

    # Check clicking on an invalid resource
    id = 'pancakes'
    response = client.put(f"/api/v1/resources/{id}/click", follow_redirects=True)
    assert (response.status_code == 404)
    assert (isinstance(response.json.get('errors').get(
            get_error_code_from_status(response.status_code)), dict))
    assert (isinstance(response.json.get('errors').get(
        get_error_code_from_status(response.status_code)).get('message'), str))

    # Check clicking on a resource that doesn't exist
    too_high = 99999999
    response = client.put(f"/api/v1/resources/{too_high}/click", follow_redirects=True)
    assert (response.status_code == 404)
    assert (isinstance(response.json.get('errors').get(
        get_error_code_from_status(response.status_code)), dict))
    assert (isinstance(response.json.get('errors').get(
        get_error_code_from_status(response.status_code)).get('message'), str))


def test_bad_standardize_response(
        module_client, module_db, unmapped_standardize_response):
    client = module_client
    resources = client.get("api/v1/resources")

    assert (resources.status_code == 500)
    assert (resources.json['errors'] is not None)
    assert (resources.json['errors']['errors']['server-error'] is not None)


##########################################
# Authenticated Routes
##########################################


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


def test_create_resource(
        module_client, module_db, fake_auth_from_oc, fake_algolia_save):
    client = module_client

    # Happy Path
    apikey = get_api_key(client)
    response = create_resource(client, apikey)
    assert (response.status_code == 200)
    assert (isinstance(response.json['data'][0].get('id'), int))
    assert (response.json['data'][0].get('name') == "Some Name")

    # Invalid API Key Path
    response = create_resource(client, "invalidapikey")
    assert (response.status_code == 401)

    # Invalid Resource Path
    response = client.post('/api/v1/resources',
                           headers={'x-apikey': apikey})
    assert (response.status_code == 422)

    # Bogus Data
    name = False
    url = "htt://bad_url.doesnotexist"
    category = True
    languages = False
    paid = "Bad Data"
    notes = True
    response = create_resource(client,
                               apikey,
                               name,
                               url,
                               category,
                               languages,
                               paid,
                               notes)
    assert (response.status_code == 422)

    # A String to Big for the DB
    long_string = "x" * 6501
    name = long_string
    url = long_string
    category = long_string
    languages = long_string
    paid = True
    notes = long_string
    response = create_resource(client,
                               apikey,
                               name,
                               url,
                               category,
                               languages,
                               paid,
                               notes)
    assert (response.status_code == 422)

    # Unicode Characters
    name = "😀"
    url = None
    category = None
    languages = None
    paid = True
    notes = "∞"
    response = create_resource(client,
                               apikey,
                               name,
                               url,
                               category,
                               languages,
                               paid,
                               notes)
    assert (response.status_code == 200)

    # Missing Required Fields
    response = client.post('/api/v1/resources',
                           json=[dict(notes="Missing Required fields")],
                           headers={'x-apikey': apikey})
    assert (response.status_code == 422)
    assert (isinstance(response.json.get('errors')[0]
            .get(MISSING_PARAMS), dict))
    assert (isinstance(response.json.get('errors')[0]
            .get(MISSING_PARAMS).get('message'), str))
    assert ("name" in response.json.get('errors')[0]
            .get(MISSING_PARAMS).get("params"))
    assert ("name" in response.json.get('errors')[0]
            .get(MISSING_PARAMS).get("message"))
    assert ("url" in response.json.get('errors')[0]
            .get(MISSING_PARAMS).get("params"))
    assert ("url" in response.json.get('errors')[0]
            .get(MISSING_PARAMS).get("message"))
    assert ("category" in response.json.get('errors')[0]
            .get(MISSING_PARAMS).get("params"))
    assert ("category" in response.json.get('errors')[0]
            .get(MISSING_PARAMS).get("message"))
    assert ("paid" in response.json.get('errors')[0]
            .get(MISSING_PARAMS).get("params"))
    assert ("paid" in response.json.get('errors')[0]
            .get(MISSING_PARAMS).get("message"))

    # Too many resources in the list
    response = client.post('/api/v1/resources',
                           json=[{} for x in range(0, 201)],
                           headers={'x-apikey': apikey})

    assert (response.status_code == 422)
    assert (isinstance(response.json.get("errors")[0]
            .get("too-long"), dict))
    assert (isinstance(response.json.get("errors")[0]
            .get("too-long").get("message"), str))


def test_create_multiple_resources(
        module_client, module_db, fake_auth_from_oc, fake_algolia_save):
    client = module_client
    apikey = get_api_key(client)

    # Happy Path
    url1 = f"http://example.org/{str(datetime.now())}"
    url2 = f"http://example.com/{str(datetime.now())}"
    data = [dict(
                name="Some Name",
                url=url1,
                category="New Category",
                languages=["Python", "New Language"],
                paid=False,
                notes="Some notes"),
            dict(
                name="Some Other Name",
                url=url2,
                category="Different Category",
                languages=["Python", "New Language", "JSON"],
                paid=True,
                notes="Some notes")
            ]
    response = client.post('/api/v1/resources',
                           json=data,
                           headers={'x-apikey': apikey})

    assert (response.status_code == 200)
    response_data = response.get_json().get("data")
    assert (len(response_data) == 2)
    for res in response_data:
        assert (res.get("url") == url1 or res.get("url") == url2)

    # Sad path (duplicate URL)
    data = [dict(
                name="Some Name",
                url=url1,
                category="New Category",
                languages=["Python", "New Language"],
                paid=False,
                notes="Some notes")]
    response = client.post('/api/v1/resources',
                           json=data,
                           headers={'x-apikey': apikey})
    assert (response.status_code == 422)
    assert (response.get_json().get("data") is None)
    errors = response.get_json().get("errors")
    assert (isinstance(errors, list))
    assert (errors[0].get("index") == 0)
    assert (errors[0].get("invalid-params").get("message"))
    assert (errors[0].get("invalid-params").get("resource"))
    assert (isinstance(errors[0].get("invalid-params").get("params"), list))

    # Sad path, check index
    data = [dict(
                name="Some Name",
                url="some.new.url",
                category="New Category",
                languages=["Python", "New Language"],
                paid=False,
                notes="Some notes"),
            dict(
                name="Other Name"
            )]
    response = client.post('/api/v1/resources',
                           json=data,
                           headers={'x-apikey': apikey})
    assert (response.status_code == 422)
    assert (response.get_json().get("data") is None)
    assert (response.get_json().get("errors")[0].get("index") == 1)


def test_create_resource_wrong_type(
        module_client, module_db, fake_auth_from_oc, fake_algolia_save):
    client = module_client
    apikey = get_api_key(client)
    response = client.post('/api/v1/resources',
                           json={"expected_error": "This should be a list"},
                           headers={'x-apikey': apikey})
    assert (response.status_code == 422)
    assert ("object" in response.get_json()
            .get("errors").get("invalid-type").get("message"))

    response = client.post('/api/v1/resources',
                           json=1,
                           headers={'x-apikey': apikey})
    assert (response.status_code == 422)
    assert ("int" in response.get_json()
            .get("errors").get("invalid-type").get("message"))

    response = client.post('/api/v1/resources',
                           json=1.2,
                           headers={'x-apikey': apikey})
    assert (response.status_code == 422)
    assert ("number" in response.get_json()
            .get("errors").get("invalid-type").get("message"))

    response = client.post('/api/v1/resources',
                           json=True,
                           headers={'x-apikey': apikey})
    assert (response.status_code == 422)
    assert ("boolean" in response.get_json()
            .get("errors").get("invalid-type").get("message"))

    response = client.post('/api/v1/resources',
                           json="This should be a list",
                           headers={'x-apikey': apikey})
    assert (response.status_code == 422)
    assert ("string" in response.get_json()
            .get("errors").get("invalid-type").get("message"))


def test_update_resource_wrong_type(
        module_client, module_db, fake_auth_from_oc, fake_algolia_save):
    client = module_client
    apikey = get_api_key(client)
    response = client.put('/api/v1/resources/1',
                          json=[{"expected_error": "This should be a dict"}],
                          headers={'x-apikey': apikey})
    assert (response.status_code == 422)
    assert ("array" in response.get_json()
            .get("errors").get("invalid-type").get("message"))

    response = client.put('/api/v1/resources/1',
                          json=1,
                          headers={'x-apikey': apikey})
    assert (response.status_code == 422)
    assert ("int" in response.get_json()
            .get("errors").get("invalid-type").get("message"))

    response = client.put('/api/v1/resources/1',
                          json=4.2,
                          headers={'x-apikey': apikey})
    assert (response.status_code == 422)
    assert ("number" in response.get_json()
            .get("errors").get("invalid-type").get("message"))

    response = client.put('/api/v1/resources/1',
                          json=True,
                          headers={'x-apikey': apikey})
    assert (response.status_code == 422)
    assert ("boolean" in response.get_json()
            .get("errors").get("invalid-type").get("message"))

    response = client.put('/api/v1/resources/1',
                          json="This should be a dict",
                          headers={'x-apikey': apikey})
    assert (response.status_code == 422)
    assert ("string" in response.get_json()
            .get("errors").get("invalid-type").get("message"))


def test_update_resource(
        module_client, module_db, fake_auth_from_oc, fake_algolia_save):
    client = module_client
    apikey = get_api_key(client)

    # Happy Path
    response = update_resource(client, apikey)
    assert (response.status_code == 200)
    assert (response.json['data'].get('name') == "New name")

    # Paid parameter as "FALSE" instead of False
    response = update_resource(client, apikey, name="New name 2", paid="FALSE")
    assert (response.status_code == 200)
    assert (response.json['data'].get('name') == "New name 2")

    # Bogus Data
    name = False
    url = "htt://bad_url.doesnotexist"
    category = True
    languages = False
    paid = "Bad Data"
    notes = True
    response = update_resource(client,
                               apikey,
                               name,
                               url,
                               category,
                               languages,
                               paid,
                               notes)
    assert (response.status_code == 422)

    # A String to Big for the DB
    long_string = "x" * 6501
    name = long_string
    url = long_string
    category = long_string
    languages = long_string
    paid = True
    notes = long_string
    response = update_resource(client,
                               apikey,
                               name,
                               url,
                               category,
                               languages,
                               paid,
                               notes)
    assert (response.status_code == 422)

    # Unicode Characters
    name = "😀"
    url = None
    category = None
    languages = None
    paid = True
    notes = "∞"
    response = update_resource(client,
                               apikey,
                               name,
                               url,
                               category,
                               languages,
                               paid,
                               notes)
    assert (response.status_code == 200)

    # Resource not found
    response = client.put("/api/v1/resources/0",
                          json=dict(name="New name"),
                          headers={'x-apikey': apikey},
                          follow_redirects=True
                          )
    assert (response.status_code == 404)


def test_validate_resource(module_client, module_db, fake_auth_from_oc):
    client = module_client

    apikey = get_api_key(client)

    # Input validation
    # IntegrityError
    response = client.put(
        "/api/v1/resources/2",
        json=dict(
            name="New name",
            languages=["New language"],
            category="New Category",
            url="https://new.url",
            paid=False,
            notes="New notes"
        ),
        headers={'x-apikey': apikey}
    )

    assert (response.status_code == 422)
    assert (isinstance(response.json.get('errors')
            .get(INVALID_PARAMS), dict))
    assert (isinstance(response.json.get('errors')
            .get(INVALID_PARAMS).get('message'), str))
    assert ("url" in response.json.get('errors')
            .get(INVALID_PARAMS).get("params"))
    assert ("url" in response.json.get('errors')
            .get(INVALID_PARAMS).get("message"))

    # Type Conversion
    response = client.put("/api/v1/resources/2",
                          json=dict(
                              name=12345,
                              url="https://good.url",
                              category=56789,
                              paid="false",
                          ),
                          headers={'x-apikey': apikey}
                          )

    assert (response.status_code == 200)
    assert (response.json['data'].get('name') == "12345")
    assert (response.json['data'].get('category') == "56789")
    assert (response.json['data'].get('paid') is False)

    # TypeError
    response = client.put("/api/v1/resources/2",
                          json=dict(url=1),
                          headers={'x-apikey': apikey})

    assert (response.status_code == 422)
    assert (isinstance(response.json.get('errors')
            .get(INVALID_PARAMS), dict))
    assert (isinstance(response.json.get('errors')
            .get(INVALID_PARAMS).get('message'), str))
    assert ("url" in response.json.get('errors')
            .get(INVALID_PARAMS).get("params"))
    assert ("url" in response.json.get('errors')
            .get(INVALID_PARAMS).get("message"))

    response = client.put("/api/v1/resources/2",
                          json=dict(
                              name=False,
                              languages=1,
                          ),
                          headers={'x-apikey': apikey}
                          )

    assert (response.status_code == 422)
    assert (isinstance(response.json.get('errors')
            .get(INVALID_PARAMS), dict))
    assert (isinstance(response.json.get('errors')
            .get(INVALID_PARAMS).get('message'), str))
    assert ("name" in response.json.get('errors')
            .get(INVALID_PARAMS).get("params"))
    assert ("name" in response.json.get('errors')
            .get(INVALID_PARAMS).get("message"))
    assert ("languages" in response.json.get('errors')
            .get(INVALID_PARAMS).get("params"))
    assert ("languages" in response.json.get('errors')
            .get(INVALID_PARAMS).get("message"))

    response = client.put("/api/v1/resources/2",
                          headers={'x-apikey': apikey}
                          )
    assert (isinstance(response.json.get('errors')[0]
            .get(MISSING_BODY), dict))
    assert (isinstance(response.json.get('errors')[0]
            .get(MISSING_BODY).get('message'), str))

    response = client.put(
        "api/v1/resources/1",
        data='',
        content_type='application/json',
        headers={'x-apikey': apikey},
        follow_redirects=True
    )
    assert (response.status_code == 422)
    assert (isinstance(response.json.get('errors')[0]
            .get(MISSING_BODY), dict))
    assert (isinstance(response.json.get('errors')[0]
            .get(MISSING_BODY).get('message'), str))


def test_search(
        module_client, module_db, fake_auth_from_oc, fake_algolia_save,
        fake_algolia_search):
    client = module_client

    first_term = random_string()
    apikey = get_api_key(client)

    # Create resource and find it in the search results.
    resource = client.post(
        "/api/v1/resources",
        json=[dict(
            name=f"{first_term}",
            category="Website",
            url=f"{first_term}",
            paid=False,
        )],
        headers={'x-apikey': apikey}
    )
    result = client.get(f"/api/v1/search?q={first_term}")

    assert (resource.status_code == 200)
    assert (result.status_code == 200)
    assert (result.json['data'][0]['url'] == resource.json['data'][0].get('url'))

    # Update the resource and test that search results reflect changes
    updated_term = random_string()
    resource_id = resource.json['data'][0].get('id')
    resource = client.put(f"/api/v1/resources/{resource_id}",
                          json=dict(url=f"{updated_term}",),
                          headers={'x-apikey': apikey})

    result = client.get(f"/api/v1/search?q={updated_term}")

    assert (resource.status_code == 200)
    assert (result.status_code == 200)
    assert (result.json['data'][0]['url'] == resource.json['data'].get('url'))


def test_search_paid_filter(module_client,
                            module_db,
                            fake_auth_from_oc,
                            fake_algolia_save,
                            fake_algolia_search):
    client = module_client

    # Test on the unpaid resources
    result = client.get("/api/v1/search?paid=false")
    assert (result.status_code == 200)

    # Test on the paid resources
    result = client.get("/api/v1/search?paid=true")
    assert (result.status_code == 200)

    # Test with invalid paid attribute given ( defaults to all )
    result = client.get("/api/v1/search?paid=something")
    assert (result.status_code == 200)


def test_search_category_filter(module_client,
                                module_db,
                                fake_auth_from_oc,
                                fake_algolia_save,
                                fake_algolia_search):
    client = module_client

    # Test on book resources
    result = client.get("/api/v1/search?category=books")
    assert (result.status_code == 200)

    result = client.get("/api/v1/search?category=Books")
    assert (result.status_code == 200)

    # Test with invalid category attribute given ( defaults to all )
    result = client.get("/api/v1/search?category=")
    assert (result.status_code == 200)


def test_search_language_filter(module_client,
                                module_db,
                                fake_auth_from_oc,
                                fake_algolia_save,
                                fake_algolia_search):
    client = module_client

    # Test on Python resources
    result = client.get("/api/v1/search?languages=python")
    assert (result.status_code == 200)

    result = client.get("/api/v1/search?languages=Python")
    assert (result.status_code == 200)

    # Test on multiple languages
    result = client.get("/api/v1/search?languages=python&languages=javascript")
    assert (result.status_code == 200)

    # Tests with invalid languages attribute given ( defaults to all )
    result = client.get("/api/v1/search?languages=")
    assert (result.status_code == 200)

    result = client.get("/api/v1/search?languages=test&languages=")
    assert (result.status_code == 200)


def test_algolia_exception_error(module_client,
                                 module_db,
                                 fake_auth_from_oc,
                                 fake_algolia_exception):
    # Reset the FLASK_ENV to run Algolia error handling code
    environ["FLASK_ENV"] = "not_development"
    client = module_client
    first_term = random_string()
    apikey = get_api_key(client)

    response = client.get(f"/api/v1/search?q=python")

    assert (response.status_code == 500)
    assert (
        "Algolia" in response.get_json().get("errors")[0].get("algolia-failed").get(
            "message")
    )

    response = client.post("/api/v1/resources",
                           json=[dict(
                               name=f"{first_term}",
                               category="Website",
                               url=f"{first_term}",
                               paid=False,
                           )],
                           headers={'x-apikey': apikey}
                           )

    assert (response.status_code == 500)
    assert ("Algolia" in response.get_json().get("errors")[0].get("algolia-failed").get(
        "message"))

    updated_term = random_string()

    response = client.put("/api/v1/resources/1",
                          json=dict(
                              name="New name",
                              languages=["New language"],
                              category="New Category",
                              url=f"https://{updated_term}.url",
                              paid=False,
                              notes="New notes"
                          ),
                          headers={'x-apikey': apikey}
                          )

    assert (response.status_code == 500)
    assert ("Algolia" in response.get_json().get("errors")[0].get("algolia-failed").get(
        "message"))

    # Set it back to development for other tests
    environ["FLASK_ENV"] = "development"


def test_algolia_unreachable_host_error(module_client,
                                        module_db,
                                        fake_auth_from_oc,
                                        fake_algolia_unreachable_host,):
    # Reset the FLASK_ENV to run Algolia error handling code
    environ["FLASK_ENV"] = "not_development"
    client = module_client
    first_term = random_string()
    apikey = get_api_key(client)

    response = client.get("/api/v1/search?q=python")

    assert (response.status_code == 500)
    assert ("Algolia" in response.get_json().get("errors")[0].get("algolia-failed").get(
        "message"))

    response = client.post("/api/v1/resources",
                           json=[dict(
                               name=f"{first_term}",
                               category="Website",
                               url=f"{first_term}",
                               paid=False,
                           )],
                           headers={'x-apikey': apikey})

    assert (response.status_code == 500)
    assert ("Algolia" in response.get_json().get("errors")[0].get("algolia-failed").get(
        "message"))

    updated_term = random_string()

    response = client.put("/api/v1/resources/1",
                          json=dict(
                              name="New name",
                              languages=["New language"],
                              category="New Category",
                              url=f"https://{updated_term}.url",
                              paid=False,
                              notes="New notes"
                          ),
                          headers={'x-apikey': apikey}
                          )

    assert (response.status_code == 500)
    assert ("Algolia" in response.get_json().get("errors")[0].get("algolia-failed").get(
        "message"))

    # Set it back to development for other tests
    environ["FLASK_ENV"] = "development"


def test_bad_requests(module_client, module_db, fake_auth_from_oc, fake_algolia_save):
    client = module_client

    apikey = get_api_key(client)
    bad_json = "{\"test\": \"bad json\" \"test2\": \"still bad\"}"
    response = client.post(
        "api/v1/resources",
        data=bad_json,
        content_type='application/json',
        headers={'x-apikey': apikey},
        follow_redirects=True
    )
    assert (response.status_code == 400)
    assert (isinstance(response.json, dict))


def false_validation(module_client,
                     module_db,
                     fake_auth_from_oc,
                     fake_algolia_save,
                     fake_validate_resource):
    # Given the validate_resource method fails to catch errors
    # When we commit the resource to the database
    # Then the api returns a 422 response

    client = module_client
    first_term = random_string()
    apikey = get_api_key(client)

    resource = client.post("/api/v1/resources",
                           json=[dict(
                               name=f"{first_term}",
                               category="Website",
                               url=f"{first_term}",
                               paid=False,
                           )],
                           headers={'x-apikey': apikey}
                           )

    assert (resource.status_code == 200)

    id = resource.json['data'].get("id")

    resource = client.post("/api/v1/resources",
                           json=dict(
                               name=f"{first_term}",
                               category="Website",
                               url=f"{first_term}",
                               paid=False,
                           ),
                           headers={'x-apikey': apikey}
                           )

    assert (resource.status_code == 422)
    assert (resource.json['data'].get("errors") is not None)
    assert (resource.json['data'].get("errors")[
            get_error_code_from_status(resource.status_code)] ==
            msg_map[resource.status_code])

    resource = client.put(f"/api/v1/resources/{id}",
                          json=dict(
                              name="New name",
                              languages=["New language"],
                              category="New Category",
                              url=f"{first_term}",
                              paid=False,
                              notes="New notes"
                          ),
                          headers={'x-apikey': apikey}
                          )

    assert (resource.status_code == 422)
    assert (resource.json['data'].get("errors") is not None)
    assert (resource.json['data'].get("errors")[
            get_error_code_from_status(resource.status_code)] ==
            msg_map[resource.status_code])


def test_commit_errors(
        module_client, module_db, fake_auth_from_oc,
        fake_commit_error, fake_algolia_save):
    client = module_client
    apikey = get_api_key(client)

    response = client.put(
        "/api/v1/resources/1",
        json=dict(name="New name"),
        headers={'x-apikey': apikey}
    )
    assert (response.status_code == 500)

    response = create_resource(client, apikey)
    assert (response.status_code == 500)


def test_key_query_error(
        module_client, module_db, fake_auth_from_oc, fake_key_query_error):
    client = module_client
    response = client.post('api/v1/apikey', json=dict(
        email="test@example.org",
        password="supersecurepassword"
    ))
    assert (response.status_code == 500)


def test_internal_server_error_handler(
        module_client, module_db, fake_paginated_data_error):
    client = module_client

    response = client.get('api/v1/resources')
    assert (response.status_code == 500)
    assert (isinstance(response.json.get('errors')
            .get(get_error_code_from_status(response.status_code)), dict))
    assert (isinstance(response.json.get('errors')
            .get(get_error_code_from_status(response.status_code)).get('message'), str))

    response = client.get('api/v1/languages')
    assert (response.status_code == 500)
    assert (isinstance(response.json.get('errors')
            .get(get_error_code_from_status(response.status_code)), dict))
    assert (isinstance(response.json.get('errors')
            .get(get_error_code_from_status(response.status_code)).get('message'), str))

    response = client.get('api/v1/categories')
    assert (response.status_code == 500)
    assert (isinstance(response.json.get('errors')
            .get(get_error_code_from_status(response.status_code)), dict))
    assert (isinstance(response.json.get('errors')
            .get(get_error_code_from_status(response.status_code)).get('message'), str))


def test_method_not_allowed_handler(module_client):
    client = module_client

    response = client.patch('api/v1/resources')
    assert (response.status_code == 405)
    assert (isinstance(response.json.get('errors')
            .get(get_error_code_from_status(response.status_code)), dict))
    assert (isinstance(response.json.get('errors')
            .get(get_error_code_from_status(response.status_code)).get('message'), str))


##########################################
# Other Routes
##########################################

def test_health_check(module_client):
    response = module_client.get('/healthz')
    assert (response.status_code == 200)
    print(response.get_json())
    assert (response.get_json().get("application").get("status") == "ok")


# This method must come last if using the persistent client and db
def test_rate_limit(module_client, module_db):
    client = module_client

    for _ in range(50):
        client.get('api/v1/resources')

    # Response should be a failure on request 51
    response = client.get('api/v1/resources')
    assert(response.status_code == 429)
    assert (isinstance(response.json.get('errors')
            .get(get_error_code_from_status(response.status_code)), dict))
    assert (isinstance(response.json.get('errors')
            .get(get_error_code_from_status(response.status_code)).get('message'), str))


##########################################
# Helpers
##########################################


def create_resource(client,
                    apikey,
                    name=None,
                    url=None,
                    category=None,
                    languages=None,
                    paid=None,
                    notes=None,
                    headers=None,
                    endpoint='/api/v1/resources'):
    return client.post(endpoint,
                       json=[dict(
                           name="Some Name" if not name else name,
                           url=f"http://example.org/{str(datetime.now())}"
                                if not url else url,
                           category="New Category" if not category else category,
                           languages=[
                               "Python", "New Language"
                            ] if not languages else languages,
                           paid=False if not paid else paid,
                           notes="Some notes" if not notes else notes)],
                       headers={'x-apikey': apikey} if not headers else headers)


def update_resource(client,
                    apikey,
                    name=None,
                    url=None,
                    category=None,
                    languages=None,
                    paid=None,
                    notes=None,
                    headers=None,
                    endpoint='/api/v1/resources/1'):
    return client.put(endpoint,
                      json=dict(
                            name="New name" if not name else name,
                            url="https://new.url" if not url else url,
                            category="New Category" if not category else category,
                            languages=["New language"] if not languages else languages,
                            paid=False if not paid else paid,
                            notes="New notes" if not notes else notes),
                      headers={'x-apikey': apikey} if not headers else headers)


def get_api_key(client):
    response = client.post('api/v1/apikey', json=dict(
        email="test@example.org",
        password="supersecurepassword"
    ))

    return response.json['data'].get('apikey')
