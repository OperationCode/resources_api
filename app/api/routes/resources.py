from datetime import datetime

from algoliasearch.exceptions import AlgoliaUnreachableHostException, AlgoliaException
from dateutil import parser
from flask import request, redirect
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError

from app import utils as utils, db, index
from app.api import bp
from app.api.auth import authenticate
from app.api.routes.utils import latency_summary, failures_counter, logger
from app.api.validations import requires_body, validate_resource
from app.models import Resource, Language, Category
from configs import Config


# Routes
@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/resources', methods=['GET'], endpoint='get_resources')
def resources():
    return get_resources()


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/resources', methods=['POST'], endpoint='create_resource')
@requires_body
@authenticate
def post_resources():
    validation_errors = validate_resource(request)

    if validation_errors:
        return utils.standardize_response(payload=validation_errors, status_code=422)
    return create_resource(request.get_json(), db)


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/resources/<int:id>', methods=['GET'], endpoint='get_resource')
def resource(id):
    return get_resource(id)


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/resources/<int:id>', methods=['PUT'], endpoint='update_resource')
@requires_body
@authenticate
def put_resource(id):
    validation_errors = validate_resource(request, id)

    if validation_errors:
        return utils.standardize_response(payload=validation_errors, status_code=422)
    return update_resource(id, request.get_json(), db)


# Business Logic
def get_resources():
    """
    Gets a paginated list of resources.

    If the URL parameters `language` or `category` are found
    in the request, the list will be filtered by these parameters.

    The filters are case insensitive.
    """
    resource_paginator = utils.Paginator(Config.RESOURCE_PAGINATOR, request)

    # Fetch the filter params from the url, if they were provided.
    language = request.args.get('language')
    category = request.args.get('category')
    updated_after = request.args.get('updated_after')
    paid = request.args.get('paid')

    q = Resource.query

    # Filter on language
    if language:
        q = q.filter(
            Resource.languages.any(
                Language.name.ilike(language)
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


def create_resource(json, db):
    langs, categ = get_attributes(json)
    new_resource = Resource(
        name=json.get('name'),
        url=json.get('url'),
        category=categ,
        languages=langs,
        paid=json.get('paid'),
        notes=json.get('notes'))

    try:
        db.session.add(new_resource)
        db.session.commit()
        index.save_object(new_resource.serialize_algolia_search)

    except (AlgoliaUnreachableHostException, AlgoliaException) as e:
        logger.exception(e)
        print(f"Algolia failed to index new resource '{new_resource.name}'")

    except IntegrityError as e:
        logger.exception(e)
        return utils.standardize_response(status_code=422)

    except Exception as e:
        logger.exception(e)
        return utils.standardize_response(status_code=500)

    return utils.standardize_response(payload=dict(data=new_resource.serialize))


def get_resource(id):
    resource = Resource.query.get(id)

    if resource:
        return utils.standardize_response(payload=dict(data=(resource.serialize)))

    return redirect('/404')


def update_resource(id, json, db):
    resource = Resource.query.get(id)

    if not resource:
        return redirect('/404')

    langs, categ = get_attributes(json)
    index_object = {'objectID': id}

    try:
        logger.info(f"Updating resource. Old data: {resource.serialize}")
        if json.get('languages'):
            resource.languages = langs
            index_object['languages'] = resource.serialize['languages']
        if json.get('category'):
            resource.category = categ
            index_object['category'] = categ.name
        if json.get('name'):
            resource.name = json.get('name')
            index_object['name'] = json.get('name')
        if json.get('url'):
            resource.url = json.get('url')
            index_object['url'] = json.get('url')
        if 'paid' in json:
            paid = json.get('paid')

            # Converts "false" and "true" to their bool
            if type(paid) is str and paid.lower() in ["true", "false"]:
                paid = paid.lower().strip() == "true"
            resource.paid = paid
            index_object['paid'] = paid
        if 'notes' in json:
            resource.notes = json.get('notes')
            index_object['notes'] = json.get('notes')

        db.session.commit()

        try:
            index.partial_update_object(index_object)

        except (AlgoliaUnreachableHostException, AlgoliaException) as e:
            logger.exception(e)
            print(f"Algolia failed to update index for resource '{resource.name}'")

        return utils.standardize_response(
            payload=dict(data=resource.serialize)
        )

    except IntegrityError as e:
        logger.exception(e)
        return utils.standardize_response(status_code=422)

    except Exception as e:
        logger.exception(e)
        return utils.standardize_response(status_code=500)


def get_attributes(json):
    languages_list = Language.query.all()
    categories_list = Category.query.all()

    language_dict = {l.key(): l for l in languages_list}
    category_dict = {c.key(): c for c in categories_list}

    langs = []
    for lang in json.get('languages') or []:
        language = language_dict.get(lang)
        if not language:
            language = Language(name=lang)
        langs.append(language)
    categ = category_dict.get(json.get('category'), Category(name=json.get('category')))
    return (langs, categ)
