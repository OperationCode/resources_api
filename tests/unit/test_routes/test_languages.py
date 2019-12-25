from app.utils import get_error_code_from_status


def test_languages(module_client, module_db):
    client = module_client

    response = client.get('api/v1/languages')
    for language in response.json['data']:
        assert (isinstance(language.get('id'), int))
        assert (isinstance(language.get('name'), str))
        assert (language.get('name'))
    assert (response.json['number_of_pages'] is not None)

    # Test trying to get a page of results that doesn't exist
    too_far = 99999999
    response = client.get(
        f"api/v1/languages?page_size=100&page={too_far}", follow_redirects=True)
    assert (response.status_code == 404)
    assert (isinstance(response.json.get('errors').get(
        get_error_code_from_status(response.status_code)), dict))
    assert (isinstance(response.json.get('errors').get(
        get_error_code_from_status(response.status_code)).get('message'), str))


def test_get_single_language(module_client, module_db):
    client = module_client

    response = client.get('api/v1/languages/3')

    # Status should be OK
    assert (response.status_code == 200)

    language = response.json['data']
    assert (isinstance(language.get('name'), str))
    assert (language.get('name'))

    assert (language.get('id') == 3)


def test_single_language_out_of_bounds(module_client, module_db):
    client = module_client

    too_low = 0
    too_high = 9999
    response = client.get(f"api/v1/languages/{too_low}", follow_redirects=True)

    assert (response.status_code == 404)

    response = client.get(f"api/v1/languages/{too_high}", follow_redirects=True)

    assert (response.status_code == 404)
