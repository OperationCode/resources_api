from traceback import print_tb

from flask import request
from sqlalchemy import or_, func
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from app.api import bp
from app.models import Language, Resource, Category
from app import Config, db
from app.utils import Paginator, standardize_response
from dateutil import parser
from datetime import datetime
import logging

logger = logging.getLogger()


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


@bp.route('/resources/<int:id>/upvote', methods=['PUT'])
def upvote(id):
    return update_votes(id, 'upvotes')


@bp.route('/resources/<int:id>/downvote', methods=['PUT'])
def downvote(id):
    return update_votes(id, 'downvotes')


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
            return standardize_response(resource.serialize, None, "ok")
        else:
            return standardize_response({}, None, "ok")


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
    updated_after = request.args.get('updated_after')

    q = Resource.query

    # Filter on language
    if language:
        q = q.filter(
            Resource.languages.any(
                Language.name.ilike(language)
            )
        )

    # Filter on category
    if category:
        q = q.filter(
            Resource.category.has(
                func.lower(Category.name) == category.lower()
            )
        )

    # Filter on updated_after
    if updated_after:
        try:
            uaDate = parser.parse(updated_after)
            if uaDate > datetime.now():
                raise Exception("updated_after greater than today's date")
            uaDate = uaDate.strftime("%Y-%m-%d")
        except Exception as e:
            logger.error(e)
            message = 'The value for "updated_after" is invalid'
            error = [{"code": "bad-value", "message": message}]
            return standardize_response(None, error, "unprocessable-entity", 422)

        q = q.filter(
            or_(
                Resource.created_at >= uaDate,
                Resource.last_updated >= uaDate
            )
        )

    try:
        resource_list = [
            resource.serialize for resource in resource_paginator.items(q)
        ]
    except Exception as e:
        logger.error(e)
        return standardize_response(None, [{"code": "bad-request"}], "bad request", 400)

    return standardize_response(resource_list, None, "ok")


def get_languages():
    language_paginator = Paginator(Config.LANGUAGE_PAGINATOR, request)
    query = Language.query

    language_list = [
        language.serialize for language in language_paginator.items(query)
    ]

    return standardize_response(language_list, None, "ok")


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
        return standardize_response(category_list, None, "ok")


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


def update_votes(id, vote_direction):
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
            initial_count = getattr(resource, vote_direction)
            setattr(resource, vote_direction, initial_count+1)

            db.session.commit()

            return standardize_response(resource.serialize, None, "ok")
        else:
            return standardize_response({}, None, "ok")


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

        return standardize_response(resource.serialize, None, "ok")
    else:
        return standardize_response({}, None, "ok")


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

    return standardize_response(new_resource.serialize, None, "ok")
