from os import environ
from app.utils import random_string
from .helpers import get_api_key, assert_correct_response


def test_search(
        module_client, module_db, fake_auth_from_oc, fake_algolia_save,
        fake_algolia_search):
    client = module_client

    first_term = random_string()
    apikey = get_api_key(client)

    # Create resource and find it in the search results.
    resource = client.post(
        "/api/v1/resources",
        json=[dict(
            name=f"{first_term}",
            category="Website",
            url=f"{first_term}",
            paid=False,
        )],
        headers={'x-apikey': apikey}
    )
    result = client.get(f"/api/v1/search?q={first_term}")

    assert (resource.status_code == 200)
    assert (result.status_code == 200)
    assert (result.json['data'][0]['url'] == resource.json['data'][0].get('url'))

    # Update the resource and test that search results reflect changes
    updated_term = random_string()
    resource_id = resource.json['data'][0].get('id')
    resource = client.put(f"/api/v1/resources/{resource_id}",
                          json=dict(url=f"{updated_term}",),
                          headers={'x-apikey': apikey})

    result = client.get(f"/api/v1/search?q={updated_term}")

    assert (resource.status_code == 200)
    assert (result.status_code == 200)
    assert (result.json['data'][0]['url'] == resource.json['data'].get('url'))


def test_search_paid_filter(module_client,
                            module_db,
                            fake_auth_from_oc,
                            fake_algolia_save,
                            fake_algolia_search):
    client = module_client

    # Test on the unpaid resources
    result = client.get("/api/v1/search?paid=false")
    assert (result.status_code == 200)

    # Test on the paid resources
    result = client.get("/api/v1/search?paid=true")
    assert (result.status_code == 200)

    # Test with invalid paid attribute given ( defaults to all )
    result = client.get("/api/v1/search?paid=something")
    assert (result.status_code == 200)


def test_search_category_filter(module_client,
                                module_db,
                                fake_auth_from_oc,
                                fake_algolia_save,
                                fake_algolia_search):
    client = module_client

    # Test on book resources
    result = client.get("/api/v1/search?category=books")
    assert (result.status_code == 200)

    result = client.get("/api/v1/search?category=Books")
    assert (result.status_code == 200)

    # Test with invalid category attribute given ( defaults to all )
    result = client.get("/api/v1/search?category=")
    assert (result.status_code == 200)


def test_search_language_filter(module_client,
                                module_db,
                                fake_auth_from_oc,
                                fake_algolia_save,
                                fake_algolia_search):
    client = module_client

    # Test on Python resources
    result = client.get("/api/v1/search?languages=python")
    assert (result.status_code == 200)

    result = client.get("/api/v1/search?languages=Python")
    assert (result.status_code == 200)

    # Test on multiple languages
    result = client.get("/api/v1/search?languages=python&languages=javascript")
    assert (result.status_code == 200)

    # Tests with invalid languages attribute given ( defaults to all )
    result = client.get("/api/v1/search?languages=")
    assert (result.status_code == 200)

    result = client.get("/api/v1/search?languages=test&languages=")
    assert (result.status_code == 200)


def test_algolia_exception_error(module_client,
                                 module_db,
                                 fake_auth_from_oc,
                                 fake_algolia_exception):
    # Reset the FLASK_ENV to run Algolia error handling code
    environ["FLASK_ENV"] = "not_development"
    client = module_client
    first_term = random_string()
    apikey = get_api_key(client)

    response = client.get(f"/api/v1/search?q=python")

    assert (response.status_code == 500)
    assert (
        "Algolia" in response.get_json().get("errors")[0].get("algolia-failed").get(
            "message")
    )

    response = client.post("/api/v1/resources",
                           json=[dict(
                               name=f"{first_term}",
                               category="Website",
                               url=f"{first_term}",
                               paid=False,
                           )],
                           headers={'x-apikey': apikey}
                           )

    assert (response.status_code == 500)
    assert ("Algolia" in response.get_json().get("errors")[0].get("algolia-failed").get(
        "message"))

    updated_term = random_string()

    response = client.put("/api/v1/resources/1",
                          json=dict(
                              name="New name",
                              languages=["New language"],
                              category="New Category",
                              url=f"https://{updated_term}.url",
                              paid=False,
                              notes="New notes"
                          ),
                          headers={'x-apikey': apikey}
                          )

    assert (response.status_code == 500)
    assert ("Algolia" in response.get_json().get("errors")[0].get("algolia-failed").get(
        "message"))

    # Set it back to development for other tests
    environ["FLASK_ENV"] = "development"


def test_algolia_unreachable_host_error(module_client,
                                        module_db,
                                        fake_auth_from_oc,
                                        fake_algolia_unreachable_host,):
    # Reset the FLASK_ENV to run Algolia error handling code
    environ["FLASK_ENV"] = "not_development"
    client = module_client
    first_term = random_string()
    apikey = get_api_key(client)

    response = client.get("/api/v1/search?q=python")

    assert (response.status_code == 500)
    assert ("Algolia" in response.get_json().get("errors")[0].get("algolia-failed").get(
        "message"))

    response = client.post("/api/v1/resources",
                           json=[dict(
                               name=f"{first_term}",
                               category="Website",
                               url=f"{first_term}",
                               paid=False,
                           )],
                           headers={'x-apikey': apikey})

    assert (response.status_code == 500)
    assert ("Algolia" in response.get_json().get("errors")[0].get("algolia-failed").get(
        "message"))

    updated_term = random_string()

    response = client.put("/api/v1/resources/1",
                          json=dict(
                              name="New name",
                              languages=["New language"],
                              category="New Category",
                              url=f"https://{updated_term}.url",
                              paid=False,
                              notes="New notes"
                          ),
                          headers={'x-apikey': apikey}
                          )

    assert (response.status_code == 500)
    assert ("Algolia" in response.get_json().get("errors")[0].get("algolia-failed").get(
        "message"))

    # Set it back to development for other tests
    environ["FLASK_ENV"] = "development"


def false_validation(module_client,
                     module_db,
                     fake_auth_from_oc,
                     fake_algolia_save,
                     fake_validate_resource):
    # Given the validate_resource method fails to catch errors
    # When we commit the resource to the database
    # Then the api returns a 422 response

    client = module_client
    first_term = random_string()
    apikey = get_api_key(client)

    resource = client.post("/api/v1/resources",
                           json=[dict(
                               name=f"{first_term}",
                               category="Website",
                               url=f"{first_term}",
                               paid=False,
                           )],
                           headers={'x-apikey': apikey}
                           )

    assert (resource.status_code == 200)

    id = resource.json['data'].get("id")

    response = client.post("/api/v1/resources",
                           json=dict(
                               name=f"{first_term}",
                               category="Website",
                               url=f"{first_term}",
                               paid=False,
                           ),
                           headers={'x-apikey': apikey}
                           )

    assert_correct_response(response, 422)

    response = client.put(f"/api/v1/resources/{id}",
                          json=dict(
                              name="New name",
                              languages=["New language"],
                              category="New Category",
                              url=f"{first_term}",
                              paid=False,
                              notes="New notes"
                          ),
                          headers={'x-apikey': apikey}
                          )

    assert_correct_response(response, 422)
