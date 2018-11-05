from traceback import print_tb

from flask import request
from flask import jsonify
from sqlalchemy import and_, func
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from app.api import bp
from app.models import Language, Resource, Category
from app import Config, db
from app.utils import Paginator


# Shared
@bp.teardown_request
def teardown_request(exception=None):
    if exception:
        print('exception', exception)
        db.session.rollback()
    db.session.remove()


# Routes
@bp.route('/resources', methods=['GET', 'POST'])
def resources():
    if request.method == 'GET':
        return get_resources()
    elif request.method == 'POST':
        return create_resource(request.get_json(), db)


@bp.route('/resources/<int:id>', methods=['GET', 'PUT'])
def resource(id):
    if request.method == 'GET':
        return get_resource(id)
    elif request.method == 'PUT':
        return set_resource(id, request.get_json(), db)


@bp.route('/languages', methods=['GET'])
def languages():
    return get_languages()


@bp.route('/categories', methods=['GET'])
def categories():
    return get_categories()


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

    return jsonify(resource_list)


def get_languages():
    language_paginator = Paginator(Config.LANGUAGE_PAGINATOR, request)
    query = Language.query

    language_list = [
        language.serialize for language in language_paginator.items(query)
    ]

    return jsonify(language_list)


def get_categories():
    try:
        category_paginator = Paginator(Config.CATEGORY_PAGINATOR, request)
        query = Category.query

        category_list = [
            category.serialize for category in category_paginator.items(query)
        ]

    except Exception as e:
        print_tb(e.__traceback__)
        print(e)
        category_list = []
    finally:
        return jsonify(category_list)


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
    resource = Resource.query.get(id)
    langs, categ = get_attributes(json)

    if resource:
        if json.get('languages'):
            resource.languages = langs
        if json.get('category'):
            resource.category = categ
        if json.get('name'):
            resource.name = json.get('name')
        if json.get('url'):
            resource.url = json.get('url')
        if 'paid' in json:
            resource.paid = json.get('paid')
        if 'notes' in json:
            resource.notes = json.get('notes')

        db.session.commit()

        return jsonify(resource.serialize)
    else:
        return jsonify({})


def create_resource(json, db):
    langs, categ = get_attributes(json)
    new_resource = Resource(
        name=json.get('name'),
        url=json.get('url'),
        category=categ,
        languages=langs,
        paid=json.get('paid'),
        notes=json.get('notes'))

    db.session.add(new_resource)
    db.session.commit()

    return jsonify(new_resource.serialize)
