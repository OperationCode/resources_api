from configs import PaginatorConfig
from app.versioning import LATEST_API_VERSION
from yaml import load
from .helpers import assert_correct_response


def test_internal_server_error_handler(
        module_client,
        module_db,
        fake_language_query_error,
        fake_category_query_error,
        fake_paginated_data_error):
    client = module_client

    response = client.get('api/v1/resources')
    assert_correct_response(response, 500)

    response = client.get('api/v1/languages')
    assert_correct_response(response, 500)

    response = client.get('api/v1/categories')
    assert_correct_response(response, 500)


def test_method_not_allowed_handler(module_client):
    client = module_client

    response = client.patch('api/v1/resources')
    assert_correct_response(response, 405)


def test_paginator(module_client, module_db):
    client = module_client

    # Default page size
    response = client.get('api/v1/resources')
    assert (len(response.json['resources']) == PaginatorConfig.per_page)

    # Test page size
    response = client.get('api/v1/resources?page_size=1')
    assert (len(response.json['resources']) == 1)
    response = client.get('api/v1/resources?page_size=5')
    assert (len(response.json['resources']) == 5)
    response = client.get('api/v1/resources?page_size=10')
    assert (len(response.json['resources']) == 10)
    response = client.get('api/v1/resources?page_size=100')
    assert (len(response.json['resources']) == 100)

    # Test pages different and sequential
    first_page_resource = response.json['resources'][0]
    assert (first_page_resource.get('id') == 1)
    response = client.get('api/v1/resources?page_size=100&page=2')
    second_page_resource = response.json['resources'][0]
    assert (second_page_resource.get('id') == 101)
    response = client.get('api/v1/resources?page_size=100&page=3')
    third_page_resource = response.json['resources'][0]
    assert (third_page_resource.get('id') == 201)

    # Test bigger than max page size
    too_long = PaginatorConfig.max_page_size + 1
    response = client.get(f"api/v1/resources?page_size={too_long}")
    assert (len(response.json['resources']) == PaginatorConfig.max_page_size)
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


def test_bad_standardize_response(
        module_client, module_db, unmapped_standardize_response):
    client = module_client
    response = client.get("api/v1/resources")
    assert_correct_response(response, 500)


def test_health_check(module_client):
    response = module_client.get('/healthz')
    assert (response.status_code == 200)
    assert (response.get_json().get("application").get("status") == "ok")


def test_get_favicon(module_client):
    response = module_client.get("favicon.ico")
    assert (response.status_code == 200)


def test_get_docs(module_client):
    response = module_client.get("/")
    assert (response.status_code == 200)
    begin_html = b'<!DOCTYPE html>\n<html>\n  <head>\n'
    b'    <title>Resources API Documentation</title>\n'
    assert (response.data.startswith(begin_html))


def test_open_api_yaml(module_client):
    response = module_client.get("/openapi.yaml")
    assert (response.status_code == 200)
    open_api_yaml = load(response.data)
    assert (isinstance(open_api_yaml, dict))
    assert (open_api_yaml.get("info").get("version") == LATEST_API_VERSION)


# This method must come last if using the persistent client and db
def test_rate_limit(module_client, module_db):
    client = module_client

    for _ in range(50):
        client.get('api/v1/resources')

    # Response should be a failure on request 51
    response = client.get('api/v1/resources')
    assert_correct_response(response, 429)


# Ensure the healthz endpoint is never rate limited
def test_rate_limit_healthz(module_client, module_db):
    client = module_client

    for _ in range(50):
        client.get('/healthz')

    response = client.get('/healthz')
    assert (response.status_code == 200)
