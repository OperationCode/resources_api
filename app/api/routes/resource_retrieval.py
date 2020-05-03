from datetime import datetime

from dateutil import parser
from flask import redirect, request
from sqlalchemy import func, or_

from app import utils as utils
from app.api import bp
from app.api.routes.helpers import failures_counter, latency_summary, logger
from app.models import Category, Language, Resource
from configs import Config


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/resources', methods=['GET'], endpoint='get_resources')
def resources():
    return get_resources()


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/resources/<int:id>', methods=['GET'], endpoint='get_resource')
def resource(id):
    return get_resource(id)


def get_resources():
    """
    Gets a paginated list of resources.

    If the URL parameters `languages` or `category` are found
    in the request, the list will be filtered by these parameters.

    The filters are case insensitive.
    """
    resource_paginator = utils.Paginator(Config.RESOURCE_PAGINATOR, request)

    # Fetch the filter params from the url, if they were provided.
    languages = request.args.getlist('languages')
    if not languages:
        languages = request.args.getlist('languages[]')
    category = request.args.get('category')
    updated_after = request.args.get('updated_after')
    paid = request.args.get('paid')

    q = Resource.query

    # Filter on languages
    if languages:
        # Take the list of languages they pass in, join them all with OR
        q = q.filter(
            or_(*map(Resource.languages.any,
                     map(Language.name.ilike, languages))
                )
        )

    # Filter on category
    if category:
        q = q.filter(
            Resource.category.has(
                func.lower(Category.name) == category.lower()
            )
        )

    # Filter on updated_after
    if updated_after:
        try:
            uaDate = parser.parse(updated_after)
            if uaDate > datetime.now():
                raise Exception("updated_after greater than today's date")
            uaDate = uaDate.strftime("%Y-%m-%d")
        except Exception as e:
            logger.exception(e)
            message = 'The value for "updated_after" is invalid'
            res = {"errors": {"unprocessable-entity": {"message": message}}}
            return utils.standardize_response(payload=res, status_code=422)

        q = q.filter(
            or_(
                Resource.created_at >= uaDate,
                Resource.last_updated >= uaDate
            )
        )

    # Filter on paid
    if isinstance(paid, str) and paid.lower() in ['true', 'false']:
        paidAsBool = paid.lower() == 'true'
        q = q.filter(Resource.paid == paidAsBool)

    try:
        paginated_resources = resource_paginator.paginated_data(q)
        if not paginated_resources:
            return redirect('/404')
        resource_list = [
            resource.serialize for resource in paginated_resources.items
        ]
        pagination_details = resource_paginator.pagination_details(paginated_resources)
    except Exception as e:
        logger.exception(e)
        return utils.standardize_response(status_code=500)

    return utils.standardize_response(payload=dict(
        data=resource_list,
        **pagination_details))


def get_resource(id):
    resource = Resource.query.get(id)

    if resource:
        return utils.standardize_response(payload=dict(data=(resource.serialize)))

    return redirect('/404')
