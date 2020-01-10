
from datetime import datetime, timedelta
from .helpers import (
    create_resource, update_resource, get_api_key, set_resource_last_updated,
    assert_correct_response
)


def test_get_resources(module_client, module_db):
    client = module_client
    response = client.get('api/v1/resources')

    assert (response.status_code == 200)

    for resource in response.json['data']:
        assert (isinstance(resource.get('name'), str))
        assert (resource.get('name'))
        assert (isinstance(resource.get('url'), str))
        assert (resource.get('url'))
        assert (isinstance(resource.get('category'), str))
        assert (resource.get('category'))
        assert (isinstance(resource.get('languages'), list))
    assert (response.json['number_of_pages'] is not None)


def test_get_resources_updated_after(module_client, module_db):
    client = module_client
    ua = datetime.now() + timedelta(days=-7)
    uaString = ua.strftime('%m-%d-%Y')
    response = client.get(f"/api/v1/resources?updated_after={uaString}")
    assert (response.status_code == 200)


def test_get_resources_page_out_of_bounds(module_client, module_db):
    client = module_client
    too_far = 99999999
    response = client.get(
        f"api/v1/resources?page_size=100&page={too_far}", follow_redirects=True)
    assert_correct_response(response, 404)


def test_get_resources_post_date_failure(module_client):
    client = module_client
    # If updated_after date is after today, then should return a 422
    ua = datetime.now() + timedelta(days=1)
    uaString = ua.strftime('%m-%d-%Y')
    response = client.get(f"/api/v1/resources?updated_after={uaString}")
    assert_correct_response(response, 422)


def test_get_single_resource(module_client, module_db):
    client = module_client
    response = client.get('api/v1/resources/5')

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
    assert_correct_response(response, 404)

    response = client.get(f"api/v1/resources/{too_high}", follow_redirects=True)
    assert_correct_response(response, 404)


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


def test_paid_filter_uppercase_parameter(module_client, module_db):
    client = module_client

    response = client.get('api/v1/resources?paid=TRUE')
    assert all([res.get('paid') for res in response.json['data']])

    response = client.get('api/v1/resources?paid=FALSE')
    assert all([not res.get('paid') for res in response.json['data']])


def test_paid_filter_invalid_paid_parameter(module_client, module_db):
    client = module_client

    response = client.get('api/v1/resources?paid=na93ns8i1ns')

    assert (True in [res.get('paid') for res in response.json['data']])
    assert (False in [res.get('paid') for res in response.json['data']])


def test_language_filter(module_client, module_db):
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

    # Gibberish language returns a 404
    response = client.get('api/v1/resources?languages=gibberish', follow_redirects=True)
    assert_correct_response(response, 404)


def test_category_filter(module_client, module_db):
    client = module_client

    # Filter by category
    response = client.get('api/v1/resources?category=Back%20End%20Dev')

    for resource in response.json['data']:
        assert (resource.get('category') == "Back End Dev")

    # Gibberish category returns a 404
    response = client.get('api/v1/resources?category=gibberish', follow_redirects=True)
    assert_correct_response(response, 404)


def test_updated_after_filter(module_client,
                              module_db,
                              fake_auth_from_oc,
                              fake_algolia_save):
    client = module_client
    apikey = get_api_key(client)

    # Filter by updated_after
    filter_time = datetime.now() + timedelta(days=-1)
    set_resource_last_updated(db=module_db)

    # New resources should be the only ones returned
    create_resource(client, apikey)
    update_resource(client, apikey)
    response = client.get(f"/api/v1/resources?updated_after={filter_time}")
    assert len(response.json['data']) == 2
    for resource in response.json['data']:
        assert (
                filter_time <= datetime.strptime(resource.get('created_at'),
                                                 '%Y-%m-%d %H:%M:%S')
                or
                filter_time <= datetime.strptime(resource.get('last_updated'),
                                                 '%Y-%m-%d %H:%M:%S')
        )
