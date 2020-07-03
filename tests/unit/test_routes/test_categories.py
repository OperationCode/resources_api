from .helpers import assert_correct_response


def test_categories(module_client, module_db):
    client = module_client

    response = client.get('api/v1/categories')

    for category in response.json['categories']:
        assert (isinstance(category.get('id'), int))
        assert (isinstance(category.get('name'), str))
        assert (category.get('name'))
    assert (response.json['total_count'] is not None)


def test_get_single_category(module_client, module_db):
    client = module_client

    response = client.get('api/v1/categories/4')

    # Status should be OK
    assert (response.status_code == 200)

    category = response.json['category']
    assert (isinstance(category.get('name'), str))
    assert (category.get('id') == 4)


def test_get_single_category_invalid_requests(module_client, module_db):
    client = module_client

    # Check GET request to invalid category id - too low
    too_low = 0
    response = client.get(f"api/v1/categories/{too_low}", follow_redirects=True)
    assert_correct_response(response, 404)

    # Check GET request to invalid category id - too high
    too_high = 9999
    response = client.get(f"api/v1/categories/{too_high}", follow_redirects=True)
    assert_correct_response(response, 404)

    # Check GET request to invalid category id - non integer
    string = 'waffles'
    response = client.get(f"api/v1/categories/{string}", follow_redirects=True)
    assert_correct_response(response, 404)

    white_space = ' '
    response = client.get(f"api/v1/categories/{white_space}", follow_redirects=True)
    assert_correct_response(response, 404)

    symbol = '$'
    response = client.get(f"api/v1/categories/{symbol}", follow_redirects=True)
    assert_correct_response(response, 404)

    invalid = '%C0%80'
    response = client.get(f"api/v1/categories/{invalid}", follow_redirects=True)
    assert_correct_response(response, 404)

    emoji = '🤘'
    response = client.get(f"api/v1/categories/{emoji}", follow_redirects=True)
    assert_correct_response(response, 404)
