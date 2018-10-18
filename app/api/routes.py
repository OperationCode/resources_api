from traceback import print_tb

from flask import jsonify

from app.api import bp
from app.models import Resource, Language


@bp.route('/resources', methods=['GET'])
def resources():
    return get_resources()


@bp.route('/languages', methods=['GET'])
def languages():
    return get_languages()

@bp.route('/languages/<lang>', methods=['GET'])
def language(lang):
    return get_resources(lang)


def get_resources(lang=None):
    resources = {}
    try:
        if lang:
            resources = Resource.query.filter(
                Resource.languages.any(
                    Language.name.like(lang)
                )
            ).all()
        else:
            resources = Resource.query.all()

    except Exception as e:
        print_tb(e.__traceback__)
        print(e)

    finally:
        return jsonify([single_resource.serialize for single_resource in resources])


def get_languages():
    try:
        languages = Language.query.all()

    except Exception as e:
        print_tb(e.__traceback__)
        print(e)
        languages = {}
    finally:
        return jsonify([single_resource.serialize for single_resource in resources])
