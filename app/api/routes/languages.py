from flask import redirect

from app import utils as utils
from app.api import bp
from app.api.routes.helpers import failures_counter, latency_summary, logger
from app.models import Language


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/languages', methods=['GET'])
def languages():
    return get_languages()


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/languages/<int:id>', methods=['GET'], endpoint='get_language')
def language(id):
    return get_language(id)


def get_languages():
    try:
        languages = Language.query.all()

        if not languages:
            return redirect('/404')
        language_list = [
            language.serialize for language in languages
        ]
        details = {'details': {'total_count': len(languages)}}
    except Exception as e:
        logger.exception(e)
        return utils.standardize_response(status_code=500)

    return utils.standardize_response(payload=dict(
        data=language_list,
        **details),
        datatype="languages")


def get_language(id):
    language = Language.query.get(id)

    if language:
        return utils.standardize_response(
            payload=dict(data=(language.serialize)),
            datatype="language")

    return redirect('/404')
