from flask import redirect

from app import utils as utils
from app.api import bp
from app.api.routes.helpers import failures_counter, latency_summary, logger
from app.models import Category


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
        categories = Category.query.all()

        if not categories:
            return redirect('/404')
        category_list = [
            category.serialize for category in categories
        ]
        details = {'details': {'total_count': len(categories)}}
    except Exception as e:
        logger.exception(e)
        return utils.standardize_response(status_code=500)

    return utils.standardize_response(payload=dict(
        data=category_list,
        **details),
        datatype="categories")


def get_category(id):
    category = Category.query.get(id)

    if category:
        return utils.standardize_response(
            payload=dict(data=(category.serialize)),
            datatype="category")

    return redirect('/404')
