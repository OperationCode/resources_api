from flask import request, redirect
from sqlalchemy import or_, func
from sqlalchemy.exc import IntegrityError
from algoliasearch.exceptions import AlgoliaUnreachableHostException, AlgoliaException
from app.api import bp
from app.api.auth import is_user_oc_member, authenticate
from app.api.validations import validate_resource, validate_resource_list, \
    requires_body, wrong_type
from app.models import Language, Resource, Category, Key
from app import Config, db, index
from dateutil import parser
from datetime import datetime
from prometheus_client import Counter, Summary
import app.utils as utils
from os import environ


# Metrics
failures_counter = Counter('my_failures', 'Number of exceptions raised')
latency_summary = Summary('request_latency_seconds', 'Length of request')

logger = utils.setup_logger('routes_logger')


# Routes
@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/resources', methods=['GET'], endpoint='get_resources')
def resources():
    return get_resources()


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/resources', methods=['POST'], endpoint='create_resources')
@requires_body
@authenticate
def post_resources():
    json = request.get_json()

    if not isinstance(json, list):
        return wrong_type("list of resources objects", type(json))

    validation_errors = validate_resource_list(request.method, json)

    if validation_errors:
        return utils.standardize_response(payload=validation_errors, status_code=422)

    return create_resources(json, db)


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
    json = request.get_json()

    if not isinstance(json, dict):
        return wrong_type("resource object", type(json))

    validation_errors = validate_resource(request.method, json, id)

    if validation_errors:
        errors = {"errors": validation_errors}
        return utils.standardize_response(payload=errors, status_code=422)
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
@bp.route('/languages/<int:id>', methods=['GET'], endpoint='get_language')
def language(id):
    return get_language(id)


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


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/apikey', methods=['POST'], endpoint='apikey')
@requires_body
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
        message = "The email or password you submitted is incorrect"
        payload = {'errors': {"invalid-credentials": {"message": message}}}
        return utils.standardize_response(payload=payload, status_code=401)

    try:
        # We need to check the database for an existing key
        apikey = Key.query.filter_by(email=email).first()
        if not apikey:
            # Since they're already authenticated by is_oc_user(), we know we
            # can generate an API key for them if they don't already have one
            return utils.create_new_apikey(email, logger)
        logger.info(apikey.serialize)
        return utils.standardize_response(payload=dict(data=apikey.serialize))
    except Exception as e:
        logger.exception(e)
        return utils.standardize_response(status_code=500)


# Helpers
def get_resource(id):
    resource = Resource.query.get(id)

    if resource:
        return utils.standardize_response(payload=dict(data=(resource.serialize)))

    return redirect('/404')


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


def search_results():
    term = request.args.get('q', '', str)
    page = request.args.get('page', 0, int)
    page_size = request.args.get('page_size', Config.RESOURCE_PAGINATOR.per_page, int)

    # Fetch the filter params from the url, if they were provided.
    paid = request.args.get('paid')
    category = request.args.get('category')
    languages = request.args.getlist('languages')
    filters = []

    # Filter on paid
    if paid:
        paid = paid.lower()
        # algolia filters boolean attributes with either 0 or 1
        if paid == 'true':
            filters.append('paid=1')
        elif paid == 'false':
            filters.append('paid=0')

    # Filter on category
    if category:
        # to not let double quotes conflict with algolia filter format
        category = category.replace('"', "'")

        filters.append(
            f'category: "{category}"'
        )

    # Filter on languages
    if languages and '' not in languages:
        for i, _ in enumerate(languages):
            # to not let double quotes conflict with algolia filter format
            languages[i] = 'languages:"{}"'.format(languages[i].replace('"', "'"))

        # joining all possible language values to algolia filter query
        filters.append(f"( {' OR '.join(languages)} )")

    try:
        search_result = index.search(f'{term}', {
            'filters': " AND ".join(filters),
            'page': page,
            'hitsPerPage': page_size
        })

    except (AlgoliaUnreachableHostException, AlgoliaException) as e:
        logger.exception(e)
        msg = "Failed to get resources from Algolia"
        logger.warn(msg)
        error = {'errors': [{"algolia-failed": {"message": msg}}]}
        return utils.standardize_response(payload=error, status_code=500)

    if page >= int(search_result['nbPages']):
        return redirect('/404')

    results = [utils.format_resource_search(result) for result in search_result['hits']]

    pagination_details = {
                "pagination_details": {
                    "page": search_result['page'],
                    "number_of_pages": search_result['nbPages'],
                    "records_per_page": search_result['hitsPerPage'],
                    "total_count": search_result['nbHits'],
                }
        }
    return utils.standardize_response(payload=dict(data=results, **pagination_details))


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

    return utils.standardize_response(payload=dict(data=resource.serialize))


def add_click(id):
    resource = Resource.query.get(id)

    if not resource:
        return redirect('/404')

    initial_count = getattr(resource, 'times_clicked')
    setattr(resource, 'times_clicked', initial_count + 1)
    db.session.commit()

    return utils.standardize_response(payload=dict(data=resource.serialize))


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

        try:
            index.partial_update_object(index_object)

        except (AlgoliaUnreachableHostException, AlgoliaException) as e:
            if (environ.get("FLASK_ENV") != 'development'):
                logger.exception(e)
                msg = f"Algolia failed to update index for resource '{resource.name}'"
                logger.warn(msg)
                error = {'errors': [{"algolia-failed": {"message": msg}}]}
                return utils.standardize_response(payload=error, status_code=500)

        # Wait to commit the changes until we know that Aloglia was updated
        db.session.commit()

        return utils.standardize_response(
            payload=dict(data=resource.serialize))

    except IntegrityError as e:
        logger.exception(e)
        return utils.standardize_response(status_code=422)

    except Exception as e:
        logger.exception(e)
        return utils.standardize_response(status_code=500)


def create_resources(json, db):
    try:
        # Resources to return in the response
        created_resources = []
        # Serialized Resources to send to Algolia
        created_resources_algolia = []
        # Resource IDs to delete if Algolia fails to index
        resource_id_cache = []

        # Create each Resource in the database one by one
        for resource in json:
            langs, categ = get_attributes(resource)
            new_resource = Resource(
                name=resource.get('name'),
                url=resource.get('url'),
                category=categ,
                languages=langs,
                paid=resource.get('paid'),
                notes=resource.get('notes'))

            try:
                db.session.add(new_resource)
                db.session.commit()
                created_resources_algolia.append(new_resource.serialize_algolia_search)
                resource_id_cache.append(new_resource.id)

            except IntegrityError as e:
                logger.exception(e)
                return utils.standardize_response(status_code=422)

            except Exception as e:
                logger.exception(e)
                return utils.standardize_response(status_code=500)

            created_resources.append(new_resource.serialize)

        # Take all the created resources and save them in Algolia with one API call
        try:
            index.save_objects(created_resources_algolia)

        except (AlgoliaUnreachableHostException, AlgoliaException) as e:
            if (environ.get("FLASK_ENV") != 'development'):
                logger.exception(e)

                # Remove created resources from the db to stay in sync with Algolia
                for res_id in resource_id_cache:
                    res = Resource.query.get(res_id)
                    res.languages.clear()
                    db.session.delete(res)
                db.session.commit()

                msg = "Algolia failed to index resources"
                error = {'errors': [{"algolia-failed": {"message": msg}}]}
                return utils.standardize_response(payload=error, status_code=500)

        # Success
        return utils.standardize_response(payload=dict(data=created_resources))
    except Exception as e:
        logger.exception(e)
        return utils.standardize_response(status_code=500)
