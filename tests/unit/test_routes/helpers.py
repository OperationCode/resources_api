from datetime import datetime


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


def get_api_key(client):
    response = client.post('api/v1/apikey', json=dict(
        email="test@example.org",
        password="supersecurepassword"
    ))

    return response.json['data'].get('apikey')
