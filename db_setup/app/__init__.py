import yaml
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

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
    language_dict = {}
    category_dict = {}
    unique_resources = []

    for resource in data:
        if resource['url'] not in resource_dict:
            resource_dict[resource['url']] = True
            unique_resources.append(resource)

    for resource in unique_resources:
        language = resource.get('languages') or ''
        category = resource.get('category') or ''

        if language not in language_dict:
            language_dict[language] = Language(name=language)

        if category not in category_dict:
            category_dict[category] = Category(name=resource['category'])

        try:
            new_resource = Resource(
                name=resource['name'],
                url=resource['url'],
                category=category_dict[category],
                languages=language_dict[language],
                paid=resource.get('paid'),
                notes=resource.get('notes', ''),
                upvotes=resource.get('upvotes', 0),
                downvotes=resource.get('downvotes', 0),
                times_clicked=resource.get('times_clicked', 0))

            db.session.add(new_resource)
            db.session.commit()
        except Exception as e:
            print('exception', e)
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            print(resource)
            print(new_resource)
            break


import_resources()
print('we loaded boys')

wait = input('did it work?')
resource = Resource.query.all()
for item in resource:
    print(resource)

resource = Language.query.all()
for item in resource:
    print(resource)

resource = Category.query.all()
for item in resource:
    print(resource)


