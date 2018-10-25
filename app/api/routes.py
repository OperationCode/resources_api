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
            return jsonify(resource.serialize)
        else:
            return jsonify({})
