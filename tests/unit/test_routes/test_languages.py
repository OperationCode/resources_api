from .helpers import assert_correct_response


def test_languages(module_client, module_db):
    client = module_client

    response = client.get('api/v1/languages')
    for language in response.json['languages']:
        assert (isinstance(language.get('id'), int))
        assert (isinstance(language.get('name'), str))
        assert (language.get('name'))
    assert (response.json['number_of_pages'] is not None)


def test_languages_page_out_of_bounds(module_client, module_db):
    client = module_client
    too_far = 99999999
    response = client.get(
        f"api/v1/languages?page_size=100&page={too_far}", follow_redirects=True)
    assert_correct_response(response, 404)


def test_get_single_language(module_client, module_db):
    client = module_client

    response = client.get('api/v1/languages/3')

    # Status should be OK
    assert (response.status_code == 200)

    language = response.json['language']
    assert (isinstance(language.get('name'), str))
    assert (language.get('name'))

    assert (language.get('id') == 3)


def test_single_language_invalid_requests(module_client, module_db):
    client = module_client

    # Check GET request to invalid category id - too low
    too_low = 0
    response = client.get(f"api/v1/languages/{too_low}", follow_redirects=True)
    assert_correct_response(response, 404)

    # Check GET request to invalid category id - too high
    too_high = 9999
    response = client.get(f"api/v1/languages/{too_high}", follow_redirects=True)
    assert_correct_response(response, 404)

    # Check GET request to invalid category id - non integer
    string = 'waffles'
    response = client.get(f"api/v1/languages/{string}", follow_redirects=True)
    assert_correct_response(response, 404)

    white_space = ' '
    response = client.get(f"api/v1/languages/{white_space}", follow_redirects=True)
    assert_correct_response(response, 404)

    symbol = '$'
    response = client.get(f"api/v1/languages/{symbol}", follow_redirects=True)
    assert_correct_response(response, 404)

    invalid = '%C0%80'
    response = client.get(f"api/v1/languages/{invalid}", follow_redirects=True)
    assert_correct_response(response, 404)

    emoji = '🤘'
    response = client.get(f"api/v1/languages/{emoji}", follow_redirects=True)
    assert_correct_response(response, 404)
