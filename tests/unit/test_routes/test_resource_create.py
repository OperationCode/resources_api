from datetime import datetime
from .helpers import (
    create_resource, get_api_key, assert_missing_body,
    assert_invalid_create, assert_missing_params_create,
    assert_wrong_type
)


def test_create_resource(
        module_client, module_db, fake_auth_from_oc, fake_algolia_save):
    client = module_client

    # Happy Path
    apikey = get_api_key(client)
    response = create_resource(client, apikey)
    assert (response.status_code == 200)
    assert (isinstance(response.json['resources'][0].get('id'), int))
    assert (response.json['resources'][0].get('name') == "Some Name")

    # Empty resource object
    response = client.post('/api/v1/resources',
                           headers={'x-apikey': apikey})
    assert_missing_body(response)

    # Bogus Data
    name = False
    url = "htt://bad_url.doesnotexist"
    category = True
    languages = False
    free = "Bad Data"
    notes = True
    response = create_resource(client,
                               apikey,
                               name,
                               url,
                               category,
                               languages,
                               free,
                               notes)
    assert_invalid_create(response, ["category", "free", "notes"], 0)

    # Boolean strings that can be parsed to true or False
    name = "StringsForBoolsFalse"
    url = None
    category = None
    languages = None
    free = "FaLsE"
    notes = "Some notes"
    response = create_resource(client,
                               apikey,
                               name,
                               url,
                               category,
                               languages,
                               free,
                               notes)
    assert (response.status_code == 200)
    assert response.json['resources'][0].get('free') is False
    name = "StringsForBoolsTrue"
    url = None
    category = None
    languages = None
    free = "TrUe"
    notes = "Some notes"
    response = create_resource(client,
                               apikey,
                               name,
                               url,
                               category,
                               languages,
                               free,
                               notes)
    assert (response.status_code == 200)
    assert response.json['resources'][0].get('free') is True

    # Bad "free" data
    free = "PERHAPS"
    response = create_resource(client,
                               apikey,
                               name,
                               url,
                               category,
                               languages,
                               free,
                               notes)
    assert (response.status_code == 422)

    # A String to Big for the DB
    long_string = "x" * 6501
    name = long_string
    url = long_string
    category = long_string
    languages = long_string
    free = True
    notes = long_string
    response = create_resource(client,
                               apikey,
                               name,
                               url,
                               category,
                               languages,
                               free,
                               notes)
    assert_invalid_create(response, ["languages"], 0)

    # Unicode Characters
    name = "😀"
    url = None
    category = None
    languages = None
    free = True
    notes = "∞"
    response = create_resource(client,
                               apikey,
                               name,
                               url,
                               category,
                               languages,
                               free,
                               notes)
    assert (response.status_code == 200)

    # Missing Required Fields
    response = client.post('/api/v1/resources',
                           json=[dict(notes="Missing Required fields")],
                           headers={'x-apikey': apikey})
    assert_missing_params_create(response, ["name", "url", "category", "free"], 0)

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
                free=False,
                notes="Some notes"),
            dict(
                name="Some Other Name",
                url=url2,
                category="Different Category",
                languages=["Python", "New Language", "JSON"],
                free=True,
                notes="Some notes")
            ]
    response = client.post('/api/v1/resources',
                           json=data,
                           headers={'x-apikey': apikey})

    assert (response.status_code == 200)
    response_data = response.get_json().get("resources")
    assert (len(response_data) == 2)
    for res in response_data:
        assert (res.get("url") == url1 or res.get("url") == url2)

    # Sad path (duplicate URL)
    data = [dict(
                name="Some Name",
                url=url1,
                category="New Category",
                languages=["Python", "New Language"],
                free=False,
                notes="Some notes")]
    response = client.post('/api/v1/resources',
                           json=data,
                           headers={'x-apikey': apikey})
    assert (response.status_code == 422)
    assert (response.get_json().get("resources") is None)
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
                free=False,
                notes="Some notes"),
            dict(
                name="Other Name"
            )]
    response = client.post('/api/v1/resources',
                           json=data,
                           headers={'x-apikey': apikey})
    assert (response.status_code == 422)
    assert (response.get_json().get("resources") is None)
    assert (response.get_json().get("errors")[0].get("index") == 1)


def test_create_resource_wrong_type(
        module_client, module_db, fake_auth_from_oc, fake_algolia_save):
    client = module_client
    apikey = get_api_key(client)
    response = client.post('/api/v1/resources',
                           json={"expected_error": "This should be a list"},
                           headers={'x-apikey': apikey})
    assert_wrong_type(response, "object")

    response = client.post('/api/v1/resources',
                           json=1,
                           headers={'x-apikey': apikey})
    assert_wrong_type(response, "int")

    response = client.post('/api/v1/resources',
                           json=1.2,
                           headers={'x-apikey': apikey})
    assert_wrong_type(response, "number")

    response = client.post('/api/v1/resources',
                           json=True,
                           headers={'x-apikey': apikey})
    assert_wrong_type(response, "boolean")

    response = client.post('/api/v1/resources',
                           json="This should be a list",
                           headers={'x-apikey': apikey})
    assert_wrong_type(response, "string")


def test_false_validation():
    # Given the validate_resource method fails to catch errors
    # When we commit the resource to the database
    # Then the api returns a 422 response

    # TODO: implement
    pass
