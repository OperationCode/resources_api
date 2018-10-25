from traceback import print_tb

from flask import request
from flask import jsonify
from sqlalchemy import exc, and_, func
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from app.api import bp
from app.models import Language, Resource, Category
from app import Config
from app.utils import Paginator


# Routes
@bp.route('/resources', methods=['GET'])
def resources():
    return get_resources()


@bp.route('/resources/<int:id>', methods=['GET', 'PUT'])
def resource(id, category=None, languages=[], name=None, url=None,
             paid=False, notes=None):
    if request.method == 'GET':
        return get_resource(id)
    elif request.method == 'PUT':
        param_list = [category, languages, name, url, paid, notes]
        return set_resource(id, param_list, request.args)


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


def set_resource(id, param_list, args):
    resource = None
    param_names = ['category', 'languages', 'name', 'url', 'paid', 'notes']
    for index in range(len(param_names)):
        if args.get(param_names[index]):
            param_list[index] = args.get(param_names[index])
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
            for position in range(len(param_names)):
                resource[param_names[position]] = param_list[position]
            try:
                db.session.commit()
            except exc.SQLAlchemyError as e:
                db.session.rollback()
                print('Flask SQLAlchemy Exception:', e)
                print(resource)
            return jsonify(resource.serialize)
        else:
            return jsonify({})
