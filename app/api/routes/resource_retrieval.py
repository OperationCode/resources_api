from datetime import datetime

from dateutil import parser
from flask import redirect, request, g
from sqlalchemy import func, or_, text

from app import utils as utils
from app.api import bp
from app.api.auth import authenticate
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


@authenticate(allow_no_auth_key=True)
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
    category = request.args.get('category')
    updated_after = request.args.get('updated_after')
    free = request.args.get('free')
    api_key = g.auth_key.apikey if g.auth_key else None

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
            res = {"errors": [{"unprocessable-entity": {"message": message}}]}
            return utils.standardize_response(payload=res, status_code=422)

        q = q.filter(
            or_(
                Resource.created_at >= uaDate,
                Resource.last_updated >= uaDate
            )
        )

    # Filter on free
    if isinstance(free, str) and free.lower() in ['true', 'false']:
        freeAsBool = free.lower() == 'true'
        q = q.filter(Resource.free == freeAsBool)

    # Order by "getting started" category
    if not languages and not category and free is None:
        show_first = Category.query.filter(Category.name == "Getting Started").first()
        clause = (
            f" CASE resource.category_id"
            f"   WHEN {show_first.id} THEN 1"
            f"   ELSE 2"
            f" END, id"
        )
        q = q.order_by(text(clause))

    try:
        paginated_resources = resource_paginator.paginated_data(q)
        if not paginated_resources:
            return redirect('/404')
        resource_list = [
            item.serialize(api_key)
            for item in paginated_resources.items
        ]
        details = resource_paginator.details(paginated_resources)
    except Exception as e:
        logger.exception(e)
        return utils.standardize_response(status_code=500)

    return utils.standardize_response(
        payload=dict(data=resource_list, **details),
        datatype="resources"
    )


@authenticate(allow_no_auth_key=True)
def get_resource(id):
    resource = Resource.query.get(id)
    api_key = g.auth_key.apikey if g.auth_key else None

    if resource:
        return utils.standardize_response(
            payload=dict(data=(resource.serialize(api_key))),
            datatype="resource")

    return redirect('/404')
