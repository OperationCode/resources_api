from flask import request, redirect
from sqlalchemy import or_, func
from algoliasearch.exceptions import AlgoliaUnreachableHostException, AlgoliaException
from app.api import bp
from app.api.auth import is_user_oc_member, authenticate
from app.models import Language, Resource, Category, Key
from app import Config, db, index
from app.utils import Paginator, standardize_response, setup_logger
from dateutil import parser
from datetime import datetime
from prometheus_client import Counter, Summary
import uuid

# Metrics
failures_counter = Counter('my_failures', 'Number of exceptions raised')
latency_summary = Summary('request_latency_seconds', 'Length of request')

logger = setup_logger('routes_logger')


# Routes
@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/resources', methods=['GET'], endpoint='get_resources')
def resources():
    return get_resources()


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/resources', methods=['POST'], endpoint='create_resource')
@authenticate
def post_resources():
    validation_errors = validate_resource(request.get_json())
    if validation_errors:
        return standardize_response(payload=validation_errors, status_code=422)
    return create_resource(request.get_json(), db)


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/resources/<int:id>', methods=['GET'], endpoint='get_resource')
def resource(id):
    return get_resource(id)


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/resources/<int:id>', methods=['PUT'], endpoint='update_resource')
@authenticate
def put_resource(id):
    return update_resource(id, request.get_json(), db)


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/resources/<int:id>/upvote', methods=['PUT'])
def upvote(id):
    return update_votes(id, 'upvotes')


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/resources/<int:id>/downvote', methods=['PUT'])
def downvote(id):
    return update_votes(id, 'downvotes')


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/resources/<int:id>/click', methods=['PUT'])
def update_resource_click(id):
    return add_click(id)


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/search', methods=['GET'])
def search():
    return search_results()


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/languages', methods=['GET'])
def languages():
    return get_languages()


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/categories', methods=['GET'])
def categories():
    return get_categories()


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/apikey', methods=['POST'], endpoint='apikey')
def apikey():
    """
    Verify OC membership and return an API key. The API key will be
    saved in the DB to verify use as well as returned upon subsequent calls
    to this endpoint with the same OC credentials.
    """
    json = request.get_json()
    email = json.get('email')
    password = json.get('password')
    is_oc_member = is_user_oc_member(email, password)

    if not is_oc_member:
        payload = dict(errors=["Invalid username or password"])
        return standardize_response(payload=payload, status_code=401)

    try:
        # We need to check the database for an existing key
        apikey = Key.query.filter_by(email=email).first()
        if not apikey:
            # Since they're already authenticated by is_oc_user(), we know we
            # can generate an API key for them if they don't already have one
            return create_new_apikey(email)
        logger.info(apikey.serialize)
        return standardize_response(payload=dict(data=apikey.serialize))
    except Exception as e:
        logger.exception(e)
        return standardize_response(status_code=500)


# Helpers
def get_resource(id):
    resource = Resource.query.get(id)

    if resource:
        return standardize_response(payload=dict(data=(resource.serialize)))

    return redirect('/404')


def get_resources():
    """
    Gets a paginated list of resources.

    If the URL parameters `language` or `category` are found
    in the request, the list will be filtered by these parameters.

    The filters are case insensitive.
    """
    resource_paginator = Paginator(Config.RESOURCE_PAGINATOR, request)

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
            res = dict(errors=[{'code': 'unprocessable-entity', 'message': message}])
            return standardize_response(payload=res, status_code=422)

        q = q.filter(
            or_(
                Resource.created_at >= uaDate,
                Resource.last_updated >= uaDate
            )
        )

    # Filter on paid
    if isinstance(paid, str):
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
        return standardize_response(status_code=500)

    return standardize_response(payload=dict(data=resource_list, **pagination_details))


def search_results():
    term = request.args.get('q', '', str)
    page = request.args.get('page', 0, int)
    query = Resource.query
    search_result = index.search(f'{term}', {
        'page': page,
        'hitsPerPage': request.args.get('page_size', Config.RESOURCE_PAGINATOR.per_page, int)
    })

    if page >= int(search_result['nbPages']):
        return redirect('/404')

    object_ids = [result['objectID'] for result in search_result['hits']]
    results = [r.serialize for r in query.filter(Resource.id.in_(object_ids))]

    pagination_details = {
                "pagination_details": {
                    "page": search_result['page'],
                    "number_of_pages": search_result['nbPages'],
                    "records_per_page": search_result['hitsPerPage'],
                    "total_count": search_result['nbHits'],
                }
        }
    return standardize_response(payload=dict(data=results, **pagination_details))


def get_languages():
    language_paginator = Paginator(Config.LANGUAGE_PAGINATOR, request)
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
        return standardize_response(status_code=500)

    return standardize_response(payload=dict(data=language_list, **pagination_details))


def get_categories():
    try:
        category_paginator = Paginator(Config.CATEGORY_PAGINATOR, request)
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
        return standardize_response(status_code=500)

    return standardize_response(payload=dict(data=category_list, **pagination_details))


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


def update_votes(id, vote_direction):

    resource = Resource.query.get(id)

    if not resource:
        return redirect('/404')

    initial_count = getattr(resource, vote_direction)
    setattr(resource, vote_direction, initial_count+1)
    db.session.commit()

    return standardize_response(payload=dict(data=resource.serialize))


def add_click(id):
    resource = Resource.query.get(id)

    if not resource:
        return redirect('/404')

    initial_count = getattr(resource, 'times_clicked')
    setattr(resource, 'times_clicked', initial_count + 1)
    db.session.commit()

    return standardize_response(payload=dict(data=resource.serialize))


def update_resource(id, json, db):
    resource = Resource.query.get(id)

    if not resource:
        return redirect('/404')

    langs, categ = get_attributes(json)
    index_object = {'objectID': resource.id}

    try:
        logger.info(f"Updating resource. Old data: {resource.serialize}")
        if json.get('languages'):
            resource.languages = langs
            index_object['languages'] = resource.serialize['languages']
        if json.get('category'):
            resource.category = categ
            index_object['categories'] = categ
        if json.get('name'):
            resource.name = json.get('name')
            index_object['name'] = json.get('name')
        if json.get('url'):
            resource.url = json.get('url')
            index_object['url'] = json.get('url')
        if 'paid' in json:
            resource.paid = json.get('paid')
            index_object['paid'] = json.get('paid')
        if 'notes' in json:
            resource.notes = json.get('notes')
            index_object['notes'] = json.get('notes')

        db.session.commit()

        try:
            index.partial_update_objects(index_object)

        except (AlgoliaUnreachableHostException, AlgoliaException) as e:
            logger.exception(e)
            print(f"Algolia failed to update index for resource '{resource.name}'")

        return standardize_response(
            payload=dict(data=resource.serialize)
            )

    except Exception as e:
        logger.exception(e)
        return standardize_response(status_code=500)


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

    except Exception as e:
        logger.exception(e)
        return standardize_response(status_code=500)

    return standardize_response(payload=dict(data=new_resource.serialize))


def create_new_apikey(email):
    # TODO: we should put this in a while loop in the extremely unlikely chance
    # there is a collision of UUIDs in the database. It is assumed at this point
    # in the flow that the DB was already checked for this email address, and
    # no key exists yet.
    new_key = Key(
        apikey=uuid.uuid4().hex,
        email=email
    )

    try:
        db.session.add(new_key)
        db.session.commit()

        return standardize_response(payload=dict(data=new_key.serialize))
    except Exception as e:
        logger.exception(e)
        return standardize_response(status_code=500)


def validate_resource(json):
    validation_errors = {'errors': {'type': 'validation'}}
    if not json:
        message = "A JSON body is required to use this endpoint, but none was given"
        validation_errors['errors']['message'] = message
        return validation_errors

    validation_errors['errors']['missing_params'] = []

    required = []
    for column in Resource.__table__.columns:
        if column.nullable is False and column.name != 'id':
            # strip _id from category_id
            name = column.name.replace('_id', '')
            required.append(name)

    for prop in required:
        if json.get(prop) is None:
            validation_errors['errors']['missing_params'].append(prop)

    if validation_errors['errors']['missing_params']:
        return validation_errors
