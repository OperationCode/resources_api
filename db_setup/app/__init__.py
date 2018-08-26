import yaml
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
    with open('resources.yml', 'r') as f:
        data = yaml.load(f)

    resource_dict = {}
    category_dict = {}
    unique_resources = []

    for resource in data:
        if not resource_dict.get(resource['url']):
            resource_dict[resource['url']] = True
            unique_resources.append(resource)

    # Get existing entries from DB
    try:
        resources_list = Resource.query.all()
        languages_list = Language.query.all()
    except Exception as e:
        print(e)

    language_dict = {l.name: l for l in languages_list}

    # Convert to dict for quick lookup
    existing_resources = {item.url:item for item in resources_list}

    for resource in unique_resources:
        languages = resource.get('languages') or []
        category = resource.get('category')

        for language in languages:
            if language not in language_dict:
                language_dict[language] = Language(name=language)

        if category not in category_dict:
            category_dict[category] = Category(name=category)

        existing_resource = existing_resources[resource['url']] 

        if not existing_resource:
            create_resource(resource)
        else:
            category = category_dict[category]
            langs = []
            for language in languages:
                langs.append(language_dict[language])
            update_resource(resource, existing_resource, langs, category)

def create_resource(resource):
    try:
        new_resource = Resource(
            name=resource['name'],
            url=resource['url'],
            category=category_dict[category],
            paid=resource.get('paid'),
            notes=resource.get('notes', ''),
            upvotes=resource.get('upvotes', 0),
            downvotes=resource.get('downvotes', 0),
            times_clicked=resource.get('times_clicked', 0))

        for language in languages:
            new_resource.languages.append(language_dict[language])

        db.session.add(new_resource)
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

def update_resource(resource, existing_resource, langs, category):
    # Return without updating if the resource is already up to date
    if match_resource(resource, existing_resource, langs):
        return

    try:
        existing_resource.name = resource['name']
        existing_resource.url = resource['url']
        existing_resource.category = category
        existing_resource.paid = resource.get('paid')
        existing_resource.notes = resource.get('notes', '')
        existing_resource.languages = langs

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

def match_resource(resource_dict, resource_obj, langs):
    if resource_dict['name'] != resource_obj.name:
        return False
    if resource_dict['paid'] != resource_obj.paid:
        return False
    if resource_dict['notes'] != resource_obj.notes:
        return False
    if resource_dict['category'] != resource_obj.category.name:
        return False
    if langs != resource_obj.languages:
        return False
    return True

import_resources()
print('we loaded boys')

wait = input('did it work?')
