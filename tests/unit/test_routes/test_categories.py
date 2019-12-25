from app.utils import get_error_code_from_status


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
