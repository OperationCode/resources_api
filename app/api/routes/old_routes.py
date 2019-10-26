from algoliasearch.exceptions import AlgoliaException, AlgoliaUnreachableHostException
from flask import redirect, request

import app.utils as utils
from app import Config, index
from app.api import bp
from app.api.auth import is_user_oc_member
from app.api.routes.utils import failures_counter, latency_summary, logger
from app.api.validations import requires_body
from app.models import Key


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/search', methods=['GET'])
def search():
    return search_results()


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
    if isinstance(paid, str):
        paid = paid.lower()
        # algolia filters boolean attributes with either 0 or 1
        if paid == 'true':
            filters.append('paid=1')
        elif paid == 'false':
            filters.append('paid=0')

    # Filter on category
    if isinstance(category, str):
        filters.append(
            f"category:{category}"
        )

    # Filter on languages
    if isinstance(languages, list):
        for i, _ in enumerate(languages):
            languages[i] = f"languages:{languages[i]}"

        # joining all possible language values to algolia filter query
        filters.append(f"( {' OR '.join(languages)} )")

    try:
        search_result = index.search(f'{term}', {
            'filters': "AND".join(filters),
            'page': page,
            'hitsPerPage': page_size
        })

    except (AlgoliaUnreachableHostException, AlgoliaException) as e:
        logger.exception(e)
        return utils.standardize_response(status_code=500)

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
