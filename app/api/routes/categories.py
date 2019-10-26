from flask import request, redirect

from app import utils as utils
from app.api import bp
from app.api.routes.utils import latency_summary, failures_counter, logger
from app.models import Category
from configs import Config


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/categories', methods=['GET'])
def categories():
    return get_categories()


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/categories/<int:id>', methods=['GET'], endpoint='get_category')
def category(id):
    return get_category(id)


def get_categories():
    try:
        category_paginator = utils.Paginator(Config.CATEGORY_PAGINATOR, request)
        query = Category.query

        paginated_categories = category_paginator.paginated_data(query)
        if not paginated_categories:
            return redirect('/404')
        category_list = [
            category.serialize for category in paginated_categories.items
        ]
        pagination_details = category_paginator.pagination_details(paginated_categories)
    except Exception as e:
        logger.exception(e)
        return utils.standardize_response(status_code=500)

    return utils.standardize_response(payload=dict(
        data=category_list,
        **pagination_details))


def get_category(id):
    category = Category.query.get(id)

    if category:
        return utils.standardize_response(payload=dict(data=(category.serialize)))

    return redirect('/404')
