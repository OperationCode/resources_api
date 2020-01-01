from datetime import datetime, timedelta
from app.api.validations import (
    MISSING_PARAMS, INVALID_PARAMS, MISSING_BODY, INVALID_TYPE
)
from app.models import Resource
from app.utils import get_error_code_from_status


def create_resource(client,
                    apikey,
                    name=None,
                    url=None,
                    category=None,
                    languages=None,
                    paid=None,
                    notes=None,
                    headers=None,
                    endpoint='/api/v1/resources'):
    return client.post(endpoint,
                       json=[dict(
                           name="Some Name" if not name else name,
                           url=f"http://example.org/{str(datetime.now())}"
                                if not url else url,
                           category="New Category" if not category else category,
                           languages=[
                               "Python", "New Language"
                            ] if not languages else languages,
                           paid=False if not paid else paid,
                           notes="Some notes" if not notes else notes)],
                       headers={'x-apikey': apikey} if not headers else headers)


def update_resource(client,
                    apikey,
                    name=None,
                    url=None,
                    category=None,
                    languages=None,
                    paid=None,
                    notes=None,
                    headers=None,
                    endpoint='/api/v1/resources/1'):
    return client.put(endpoint,
                      json=dict(
                            name="New name" if not name else name,
                            url="https://new.url" if not url else url,
                            category="New Category" if not category else category,
                            languages=["New language"] if not languages else languages,
                            paid=False if not paid else paid,
                            notes="New notes" if not notes else notes),
                      headers={'x-apikey': apikey} if not headers else headers)


def set_resource_last_updated(updated_time=(datetime.now() + timedelta(days=-7)),
                              id=None):
    if id is not None:
        row = Resource.query.get(id)
        row.created_at = updated_time
        row.last_updated = updated_time

    else:
        q = Resource.query
        for row in q:
            row.created_at = updated_time
            row.last_updated = updated_time


def get_api_key(client):
    response = client.post('api/v1/apikey', json=dict(
        email="test@example.org",
        password="supersecurepassword"
    ))

    return response.json['data'].get('apikey')


def assert_correct_response(response, code):
    assert (response.status_code == code)
    assert (isinstance(response.json.get('errors').get(
        get_error_code_from_status(response.status_code)), dict))
    assert (isinstance(response.json.get('errors').get(
        get_error_code_from_status(response.status_code)).get('message'), str))


def assert_correct_validation_error(response, params):
    assert (response.status_code == 422)
    assert (isinstance(response.json.get('errors')
            .get(INVALID_PARAMS), dict))
    assert (isinstance(response.json.get('errors')
            .get(INVALID_PARAMS).get('message'), str))

    for param in params:
        assert (param in response.json.get('errors')
                .get(INVALID_PARAMS).get("params"))
        assert (param in response.json.get('errors')
                .get(INVALID_PARAMS).get("message"))


def assert_missing_body(response):
    assert (response.status_code == 422)
    assert (isinstance(response.json.get('errors')[0]
            .get(MISSING_BODY), dict))
    assert (isinstance(response.json.get('errors')[0]
            .get(MISSING_BODY).get('message'), str))


def assert_invalid_create(response, params, index):
    assert (response.status_code == 422)
    assert (isinstance(response.json.get('errors')[index]
            .get(INVALID_PARAMS), dict))
    assert (isinstance(response.json.get('errors')[index]
            .get(INVALID_PARAMS).get('message'), str))

    for param in params:
        assert (response.json.get('errors')[index].get("index") == index)
        assert (param in response.json.get('errors')[index]
                .get(INVALID_PARAMS).get("params"))
        assert (param in response.json.get('errors')[index]
                .get(INVALID_PARAMS).get("message"))


def assert_missing_params_create(response, params, index):
    assert (response.status_code == 422)
    assert (isinstance(response.json.get('errors')[index]
            .get(MISSING_PARAMS), dict))
    assert (isinstance(response.json.get('errors')[index]
            .get(MISSING_PARAMS).get('message'), str))

    for param in params:
        assert (response.json.get('errors')[index].get("index") == index)
        assert (param in response.json.get('errors')[index]
                .get(MISSING_PARAMS).get("params"))
        assert (param in response.json.get('errors')[index]
                .get(MISSING_PARAMS).get("message"))


def assert_wrong_type(response, expected_type):
    assert (response.status_code == 422)
    assert (expected_type in response.get_json()
            .get("errors").get(INVALID_TYPE).get("message"))
