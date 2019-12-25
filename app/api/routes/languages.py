from flask import redirect, request

from app import utils as utils
from app.api import bp
from app.api.routes.logger import logger
from app.api.routes.metrics import failures_counter, latency_summary
from app.models import Language
from configs import Config


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
    language_paginator = utils.Paginator(Config.LANGUAGE_PAGINATOR, request)
    query = Language.query

    try:
        paginated_languages = language_paginator.paginated_data(query)
        if not paginated_languages:
            return redirect('/404')
        language_list = [
            language.serialize for language in paginated_languages.items
        ]
        pagination_details = language_paginator.pagination_details(paginated_languages)
    except Exception as e:
        logger.exception(e)
        return utils.standardize_response(status_code=500)

    return utils.standardize_response(payload=dict(
        data=language_list,
        **pagination_details))


def get_language(id):
    language = Language.query.get(id)

    if language:
        return utils.standardize_response(payload=dict(data=(language.serialize)))

    return redirect('/404')
