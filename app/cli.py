import os
import time

import yaml
import requests
from concurrent.futures import ThreadPoolExecutor

import click
from app import index, search_client
from app.api.auth import (ApiKeyError, blacklist_key,
                          find_key_by_apikey_or_email, rotate_key)
from sqlalchemy import exc

from .models import Category, Language, Resource


def import_resources(db):   # pragma: no cover
    # Step 1: Get data
    with open('resources.yml', encoding='utf-8') as f:
        data = yaml.full_load(f)

    # Step 2: Uniquify resources
    unique_resources = remove_duplicates(data)

    # Step 3: Get existing entries from db_session
    try:
        resources_list = Resource.query.all()
        languages_list = Language.query.all()
        categories_list = Category.query.all()

        # Convert to dict for quick lookup
        existing_resources = {r.key(): r for r in resources_list}
        language_dict = {l.key(): l for l in languages_list}
        category_dict = {c.key(): c for c in categories_list}
    except AttributeError as e:
        print('-------> EXCEPTION OCCURED DURING DB SETUP')
        print('-------> Most likely you need to set the '
              '"SQLALCHEMY_DATABASE_URI"')
        print(f'-------> Exception message: {e}')
        return

    # Step 4: Create/Update each resource in the db_session
    for resource in unique_resources:
        # Note: modifies the category_dict in place (bad?)
        resource['category'] = get_category(resource, category_dict)
        # Note: modifies the language_dict in place (bad?)
        resource['languages'] = get_languages(resource,
                                              language_dict)
        existing_resource = existing_resources.get(resource['url'])

        if existing_resource:
            resource == existing_resource or \
                update_resource(resource, existing_resource)
        else:
            create_resource(resource, db)

    try:
        db.session.commit()
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        print('Flask SQLAlchemy Exception:', e)
        print(resource)
    except Exception as e:
        db.session.rollback()
        print('exception', e)
        print(resource)


def remove_duplicates(data):  # pragma: no cover
    unique_resources = []
    resource_dict = {}
    for resource in data:
        if not resource_dict.get(resource['url']):
            resource_dict[resource['url']] = True
            unique_resources.append(resource)
        else:
            print(f"Encountered a duplicate resource "
                  f"in resources.yml: {resource['url']}")
    return unique_resources


def get_category(resource, category_dict):
    category = resource.get('category')

    if not category_dict.get(category):
        category_dict[category] = Category(name=category)

    return category_dict[category]


def get_languages(resource, language_dict):
    langs = []

    # Loop through languages and create a new Language
    # object for any that don't exist in the db_session
    for language in resource.get('languages') or []:
        if not language_dict.get(language):
            language_dict[language] = Language(name=language)

        # Add each Language object associated with this resource
        # to the list we'll return
        langs.append(language_dict[language])

    return langs


def create_resource(resource, db):  # pragma: no cover
    new_resource = Resource(
        name=resource['name'],
        url=resource['url'],
        category=resource['category'],
        languages=resource['languages'],
        paid=resource.get('paid'),
        notes=resource.get('notes', ''),
        upvotes=resource.get('upvotes', 0),
        downvotes=resource.get('downvotes', 0),
        times_clicked=resource.get('times_clicked', 0))

    try:
        db.session.add(new_resource)
    except Exception as e:
        print('exception', e)


def update_resource(resource, existing_resource):   # pragma: no cover
    existing_resource.name = resource['name']
    existing_resource.url = resource['url']
    existing_resource.category = resource['category']
    existing_resource.paid = resource.get('paid')
    existing_resource.notes = resource.get('notes', '')
    existing_resource.languages = resource['languages']


def reindex_all():  # pragma: no cover
    query = Resource.query
    indicies = search_client.list_indices()
    for ind in indicies['items']:
        if ind['name'] == os.environ.get('INDEX_NAME'):
            db_list = [u.serialize_algolia_search for u in query.all()]
            index.replace_all_objects(db_list)
    print("Finished Reindexing.")


def register(app, db):  # pragma: no cover
    @app.cli.group()
    def db_migrate():
        """ migration commands"""
        pass

    @app.cli.group()
    def algolia():
        """Reindex Commands"""
        pass

    @app.cli.group()
    def apikey():
        """apikey commands"""
        pass

    @app.cli.command()
    def check_bad_url():
        """check for expired resource url"""
        resources = Resource.query.all()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) \
                           AppleWebKit/537.36 (KHTML, like Gecko) \
                           Chrome/79.0.3945.117 Mobile Safari/537.36'
        }
        processes = []

        def print_bad_url(resource):
            try:
                res = requests.get(resource.url, headers=headers)
                res.status_code > 400 and \
                    print(f"resource_id: {resource.id} reource_url: {resource.url}")
            except Exception:
                print(f"resource_id: {resource.id} resource_url: {resource.url}")

        with ThreadPoolExecutor(max_workers=20) as executor:
            for resource in resources:
                processes.append(executor.submit(print_bad_url, resource))

    @db_migrate.command()
    def init():
        print(db)
        print("Populating db from resources.yml...")
        start = time.perf_counter()
        import_resources(db)
        stop = time.perf_counter()
        print("Finished populating db from resources.yml")
        print(f"Elapsed time: {(stop-start)/60} [min]")

    @db_migrate.command()
    def create_tables():
        db.create_all()

    @algolia.command()
    def reindex():
        reindex_all()

    @apikey.command()
    @click.argument('apikey_or_email')
    def blacklist(apikey_or_email):
        try:
            key = blacklist_key(apikey_or_email, True, db.session)
        except ApiKeyError as error:
            print(error.message)
            return error.error_code

        print(f'Blacklisted {key}')

    @apikey.command()
    @click.argument('apikey_or_email')
    def reactivate(apikey_or_email):
        try:
            key = blacklist_key(apikey_or_email, False, db.session)
        except ApiKeyError as error:
            print(error.message)
            return error.error_code

        print(f'Reactivated {key}')

    @apikey.command()
    @click.argument('apikey_or_email')
    def rotate(apikey_or_email):
        key = find_key_by_apikey_or_email(apikey_or_email)
        if not key:
            print('Could not find apikey or email.')
            return 1

        key = rotate_key(key, db.session)
        if not key:
            print('Error trying to rotate key.')
            return -1

        print(f'Rotated {key}')
