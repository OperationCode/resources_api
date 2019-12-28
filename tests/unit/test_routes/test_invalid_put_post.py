from .helpers import (
    create_resource, get_api_key, assert_correct_response,
    assert_correct_validation_error, assert_missing_body
)


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
    assert_correct_response(response, 400)


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
    assert_correct_response(response, 500)

    response = create_resource(client, apikey)
    assert_correct_response(response, 500)


def test_validate_resource(module_client, module_db, fake_auth_from_oc):
    client = module_client
    apikey = get_api_key(client)
    create_resource(client, apikey, url="https://new.url")

    # URL must be unique even on update
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

    assert_correct_validation_error(response, ["url"])

    # Name and category can be int
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

    # URL must be string
    response = client.put("/api/v1/resources/2",
                          json=dict(url=1),
                          headers={'x-apikey': apikey})

    assert_correct_validation_error(response, ["url"])

    # name must be string
    # languages must be array
    response = client.put("/api/v1/resources/2",
                          json=dict(
                              name=False,
                              languages=1,
                          ),
                          headers={'x-apikey': apikey}
                          )

    assert_correct_validation_error(response, ["name", "languages"])

    response = client.put("/api/v1/resources/2",
                          headers={'x-apikey': apikey}
                          )
    assert_missing_body(response)

    # Data cannot be empty
    response = client.put(
        "api/v1/resources/1",
        data='',
        content_type='application/json',
        headers={'x-apikey': apikey},
        follow_redirects=True
    )
    assert_missing_body(response)


def test_create_with_invalid_apikey(module_client, module_db):
    client = module_client
    # Invalid API Key Path
    response = create_resource(client, "invalidapikey")
    assert (response.status_code == 401)
