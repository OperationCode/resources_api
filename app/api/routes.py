from traceback import print_tb

from flask import request
from flask import jsonify
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from app.api import bp
from app.models import Language, Resource
from app import Config
from app.utils import Paginator


# Routes
@bp.route('/resources', methods=['GET'])
def resources():
    return get_resources()


@bp.route('/resources/<int:id>', methods=['GET'])
def resource_get(id):
    return get_resource(id)


@bp.route('/languages', methods=['GET'])
def languages():
    return get_languages()


@bp.route('/resources/<int:id>/<string:params>', methods=['PUT'])
def resource_set(id, params="", category=None, languages=[], name=None, url=None,
                 paid=False, notes=None):
    param_list = [category, languages, name, url, paid, notes]
    optional_params = params.split('/')
    for index in range(len(optional_params)):
        param_list[index] = optional_params[index]
    return set_resource(id, param_list)


@bp.route('/resources/<category>/<languages>/<name>/<string:url>/<string:params>',
          methods=['POST'])
def create_new(category, languages, name, url, params="", paid=False, notes=None):
    new_resource = Resource()
    optional_params = params.split('/')
    if len(optional_params) > 0:
        paid = optional_params[0]
        if len(optional_params) > 1:
            notes = optional_params[1]
    new_resource.category = category
    new_resource.languages = languages
    new_resource.name = name
    new_resource.url = url
    new_resource.paid = paid
    new_resource.notes = notes
    return jsonify(new_resource.serialize)


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
        resource_paginator = Paginator(Config.RESOURCE_PAGINATOR, Resource, request)
        resource_list = [resource.serialize for resource in resource_paginator.items]

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


def set_resource(id, param_list):
    resource = None
    try:
        resource = get_resource(id)

    except MultipleResultsFound as e:
        print_tb(e.__traceback__)
        print(e)

    except NoResultFound as e:
        print_tb(e.__traceback__)
        print(e)

    finally:
        if resource:
            resource.category = param_list[0]
            resource.languages = param_list[1]
            resource.name = param_list[2]
            resource.url = param_list[3]
            resource.paid = param_list[4]
            resource.notes = param_list[5]
            return jsonify(resource.serialize)
        else:
            return jsonify({})
