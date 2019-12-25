from app.utils import get_error_code_from_status
from configs import PaginatorConfig


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


def test_bad_standardize_response(
        module_client, module_db, unmapped_standardize_response):
    client = module_client
    resources = client.get("api/v1/resources")

    assert (resources.status_code == 500)
    assert (resources.json['errors'] is not None)
    assert (resources.json['errors']['errors']['server-error'] is not None)


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
