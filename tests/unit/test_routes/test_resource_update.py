from .helpers import (
    update_resource, get_api_key, assert_wrong_type,
    assert_correct_response
)


def test_update_votes(module_client, module_db, fake_algolia_save):
    client = module_client
    vote_direction = 'upvote'
    id = 1

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


def test_update_votes_invalid(module_client, module_db, fake_algolia_save):
    id = 'waffles'
    response = module_client.put(
        f"/api/v1/resources/{id}/upvote", follow_redirects=True)
    assert_correct_response(response, 404)
    response = module_client.put(
        f"/api/v1/resources/{id}/downvote", follow_redirects=True)
    assert_correct_response(response, 404)


def test_update_votes_out_of_bounds(module_client, module_db, fake_algolia_save):
    too_high = 99999999
    response = module_client.put(
        f"/api/v1/resources/{too_high}/upvote", follow_redirects=True)
    assert_correct_response(response, 404)
    response = module_client.put(
        f"/api/v1/resources/{too_high}/downvote", follow_redirects=True)
    assert_correct_response(response, 404)


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
    assert_correct_response(response, 404)

    # Check clicking on a resource that doesn't exist
    too_high = 99999999
    response = client.put(f"/api/v1/resources/{too_high}/click", follow_redirects=True)
    assert_correct_response(response, 404)


def test_update_resource_wrong_type(
        module_client, module_db, fake_auth_from_oc, fake_algolia_save):
    client = module_client
    apikey = get_api_key(client)
    response = client.put('/api/v1/resources/1',
                          json=[{"expected_error": "This should be a dict"}],
                          headers={'x-apikey': apikey})
    assert_wrong_type(response, "array")

    response = client.put('/api/v1/resources/1',
                          json=1,
                          headers={'x-apikey': apikey})
    assert_wrong_type(response, "int")

    response = client.put('/api/v1/resources/1',
                          json=4.2,
                          headers={'x-apikey': apikey})
    assert_wrong_type(response, "number")

    response = client.put('/api/v1/resources/1',
                          json=True,
                          headers={'x-apikey': apikey})
    assert_wrong_type(response, "boolean")

    response = client.put('/api/v1/resources/1',
                          json="This should be a dict",
                          headers={'x-apikey': apikey})
    assert_wrong_type(response, "string")


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
    assert_correct_response(response, 404)
