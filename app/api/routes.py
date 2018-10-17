from traceback import print_tb

from flask import request
from flask import jsonify
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from app.api import bp
from app.models import Resource, Language
from app import Config


# Routes
@bp.route('/resources', methods=['GET'])
def resources():
    return get_resources()


@bp.route('/resources/<int:id>', methods=['GET'])
def resource(id):
    return get_resource(id)


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
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', Config.RESOURCES_PER_PAGE, type=int)
        if page_size > Config.RESOURCE_MAX_PAGE_SIZE: page_size = Config.RESOURCE_MAX_PAGE_SIZE
        resource_paginator = Resource.query.paginate(page, page_size, False)
        resource_list = [resource.serialize for resource in resource_paginator.items]

    except Exception as e:
        print_tb(e.__traceback__)
        print(e)
        resource_list = []
    finally:
        return jsonify(resource_list)


def get_languages():
    languages = {}

    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', Config.LANGUAGES_PER_PAGE, type=int)
        if page_size > Config.LANGUAGES_MAX_PAGE_SIZE: page_size = Config.LANGUAGES_MAX_PAGE_SIZE
        language_paginator = Language.query.paginate(page, page_size, False)
        language_list = [language.serialize for language in language_paginator.items]

    except Exception as e:
        print_tb(e.__traceback__)
        print(e)
        language_list = []
    finally:
        return jsonify(language_list)
