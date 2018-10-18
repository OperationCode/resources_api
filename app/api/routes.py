from traceback import print_tb

from flask import jsonify
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from app.api import bp
from app.models import Resource, Language


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
    resources = {}
    try:
        resources = Resource.query.all()

    except Exception as e:
        print_tb(e.__traceback__)
        print(e)

    finally:
        return jsonify([single_resource.serialize for single_resource in resources])


def get_languages():
    languages = {}

    try:
        languages = Language.query.all()

    except Exception as e:
        print_tb(e.__traceback__)
        print(e)

    finally:
        return jsonify([language.name for language in languages])
