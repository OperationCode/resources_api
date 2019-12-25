from datetime import datetime
from app.utils import get_error_code_from_status
from app.api.validations import MISSING_PARAMS, INVALID_PARAMS, MISSING_BODY
from .helpers import create_resource, update_resource, get_api_key


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
