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
        resource_paginator = Paginator(Config.RESOURCE_PAGINATOR, Resource, request)
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
        language_paginator = Paginator(Config.LANGUAGE_PAGINATOR, Language, request)
        language_list = [language.serialize for language in language_paginator.items]

    except Exception as e:
        print_tb(e.__traceback__)
        print(e)
        language_list = []
    finally:
        return jsonify(language_list)
