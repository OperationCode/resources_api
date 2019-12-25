
from configs import PaginatorConfig
from datetime import datetime, timedelta
from app.utils import get_error_code_from_status
from app.versioning import LATEST_API_VERSION
from yaml import load


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


def test_get_docs(module_client):
    response = module_client.get("/")
    assert (response.status_code == 200)


def test_open_api_yaml(module_client):
    response = module_client.get("/openapi.yaml")
    assert (response.status_code == 200)
    open_api_yaml = load(response.data)
    assert (isinstance(open_api_yaml, dict))
    assert (open_api_yaml.get("info").get("version") == LATEST_API_VERSION)


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
