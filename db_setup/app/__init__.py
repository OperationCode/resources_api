import yaml
import time
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc

from configs import Config

app = Flask(__name__)

app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from .models import Resource, Category, Language


def import_resources():
    # Step 1: Get data
    with open('resources.yml', 'r') as f:
        data = yaml.load(f)

    # Step 2: Uniquify resources
    unique_resources = remove_duplicates(data) 

    # Step 3: Get existing entries from DB
    try:
        resources_list = Resource.query.all()
        languages_list = Language.query.all()
        categories_list = Category.query.all()

        # Convert to dict for quick lookup
        existing_resources = {r.key(): r for r in resources_list}
        language_dict = {l.key(): l for l in languages_list}
        category_dict = {c.key(): c for c in categories_list}
    except Exception as e:
        print(e)

    # Step 4: Create/Update each resource in the DB
    for resource in unique_resources:
        resource['category'] = get_category(resource, category_dict) # Note: modifies the category_dict in place (bad?)
        resource['languages'] = get_languages(resource, language_dict) # Note: modifies the language_dict in place (bad?)
        existing_resource = existing_resources.get(resource['url'])

        if existing_resource:
            resource == existing_resource or update_resource(resource, existing_resource)
        else:
            create_resource(resource)

    try:
        db.session.commit()
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        print('Flask SQLAlchemy Exception:', e)
        template = "An SQLAlchemy exception of type {0} occurred. Arguments:\n{1!r}"
        print(resource)
    except Exception as e:
        db.session.rollback()
        print('exception', e)
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        print(resource)

def remove_duplicates(data):
    unique_resources = []
    resource_dict = {}
    for resource in data:
        if not resource_dict.get(resource['url']):
            resource_dict[resource['url']] = True
            unique_resources.append(resource)
        else:
            print(f"Encountered a duplicate resource in resources.yml: {resource['url']}")
    return unique_resources

def get_category(resource, category_dict):
    category = resource.get('category')

    if not category_dict.get(category):
        category_dict[category] = Category(name=category)

    return category_dict[category]

def get_languages(resource, language_dict):
    langs = []

    # Loop through languages and create a new Language
    # object for any that don't exist in the DB
    for language in resource.get('languages') or []:
        if not language_dict.get(language):
            language_dict[language] = Language(name=language)

        # Add each Language object associated with this resource
        # to the list we'll return
        langs.append(language_dict[language])

    return langs

def create_resource(resource):
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

def update_resource(resource, existing_resource):
    existing_resource.name = resource['name']
    existing_resource.url = resource['url']
    existing_resource.category = resource['category']
    existing_resource.paid = resource.get('paid')
    existing_resource.notes = resource.get('notes', '')
    existing_resource.languages = resource['languages']

start = time.perf_counter()
import_resources()
stop = time.perf_counter()
print('Finished populating DB from resources.yml')
print("Elapsed time: %.1f [min]" % ((stop-start)/60))
