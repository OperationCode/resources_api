from traceback import print_tb

from flask import request
from flask import jsonify
from sqlalchemy import exc, and_, func
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from app.api import bp
from app.models import Language, Resource, Category
from app import Config, db
from app.utils import Paginator


# Routes
@bp.route('/resources', methods=['GET'])
def resources():
    return get_resources()


@bp.route('/resources/<int:id>', methods=['GET', 'PUT', 'POST'])
def resource(id):
    if request.method == 'GET':
        return get_resource(id)
    elif request.method == 'PUT':
        return set_resource(id, request.get_json(), db)
    elif request.method == 'POST':
        return create_resource(request.get_json(), db)


@bp.route('/languages', methods=['GET'])
def languages():
    return get_languages()


# Helpers
def get_resource(id):
    resource = None
    try:
        resource = Resource.query.get(id)

    except MultipleResultsFound as e:
        print_tb(e.__traceback__)
        print(e)

    except NoResultFound as e:
        print_tb(e.__traceback__)
        print(e)

    finally:
        if resource:
            return jsonify(resource.serialize)
        else:
            return jsonify({})


def get_resources():
    """
    Gets a paginated list of resources.

    If the URL parameters `language` or `category` are found
    in the request, the list will be filtered by these parameters.

    The filters are case insensitive.
    """
    try:
        resource_paginator = Paginator(Config.RESOURCE_PAGINATOR, request)

        # Fetch the filter params from the url, if they were provided.
        language = request.args.get('language')
        category = request.args.get('category')

        # Filter on language
        if language and not category:
            query = Resource.query.filter(
                Resource.languages.any(
                    Language.name.ilike(language)
                )
            )

        # Filter on category
        elif category and not language:
            query = Resource.query.filter(
                Resource.category.has(
                    func.lower(Category.name) == category.lower()
                )
            )

        # Filter on both
        elif category and language:
            query = Resource.query.filter(
                and_(
                    Resource.languages.any(
                        Language.name.ilike(language)
                    ),
                    Resource.category.has(
                        func.lower(Category.name) == category.lower()
                    )
                )
            )

        # No filters
        else:
            query = Resource.query

        resource_list = [
            resource.serialize for resource in resource_paginator.items(query)
        ]

    except Exception as e:
        print_tb(e.__traceback__)
        print(e)
        resource_list = []
    finally:
        return jsonify(resource_list)


def get_languages():
    try:
        language_paginator = Paginator(Config.LANGUAGE_PAGINATOR, Language, request)
        language_list = [language.serialize for language in language_paginator.items]

    except Exception as e:
        print_tb(e.__traceback__)
        print(e)
        language_list = []
    finally:
        return jsonify(language_list)


def get_attributes(json):
    languages_list = Language.query.all()
    categories_list = Category.query.all()

    language_dict = {l.key(): l for l in languages_list}
    category_dict = {c.key(): c for c in categories_list}

    langs = []
    for lang in json.get('languages') or []:
        language = language_dict.get(lang)
        if not language:
            language = Language(name=lang)
        langs.append(language)
    categ = category_dict.get(json.get('category'), Category(name=json.get('category')))
    return (langs, categ)


def set_resource(id, json, db):
    resource = None
    try:
        resource = Resource.query.get(id)

    except MultipleResultsFound as e:
        print_tb(e.__traceback__)
        print(e)

    except NoResultFound as e:
        print_tb(e.__traceback__)
        print(e)

    finally:
        if resource:
            if json.get('languages'):
                resource.languages = get_attributes(json)[0]
            if json.get('category'):
                resource.category = get_attributes(json)[1]
            if json.get('name'):
                resource.name = json.get('name')
            if json.get('url'):
                resource.url = json.get('url')
            if json.get('paid'):
                resource.paid = json.get('paid')
            if json.get('notes'):
                resource.notes = json.get('notes')
            try:
                db.session.commit()
            except exc.SQLAlchemyError as e:
                db.session.rollback()
                print('Flask SQLAlchemy Exception:', e)
                print(resource)
            return jsonify(resource.serialize)
        else:
            return jsonify({})


def create_resource(json, db):
    new_resource = Resource(
        name=json.get('name'),
        url=json.get('url'),
        category=get_attributes(json)[1],
        languages=get_attributes(json)[0],
        paid=json.get('paid'),
        notes=json.get('notes'),
        upvotes=None,
        downvotes=None,
        times_clicked=None)

    try:
        db.session.add(new_resource)
    except Exception as e:
        print('exception', e)
    return jsonify(new_resource.serialize)
