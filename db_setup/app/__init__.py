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

    for resource in data:

        try:
            new_resource = Resource(
                name=resource['name'],
                url=resource['url'],
                category=Category(name=resource['category']),
                languages=Language(name=resource.get('languages','')),
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
            # message = template.format(type(e).__name__, e.args)
            # print(message)
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


