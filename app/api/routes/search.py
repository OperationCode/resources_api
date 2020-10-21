from algoliasearch.exceptions import AlgoliaException, AlgoliaUnreachableHostException
from flask import redirect, request

from app import index, utils as utils
from app.api import bp
from app.api.routes.helpers import failures_counter, latency_summary, logger
from configs import Config


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/search', methods=['GET'])
def search():
    return search_results()


def search_results():
    term = request.args.get('q', '', str)
    page = request.args.get('page', 0, int)
    page_size = request.args.get('page_size', Config.RESOURCE_PAGINATOR.per_page, int)

    # Fetch the filter params from the url, if they were provided.
    free = request.args.get('free')
    category = request.args.get('category')
    languages = request.args.getlist('languages')
    filters = []

    # Filter on free
    if free:
        free = free.lower()
        # algolia filters boolean attributes with either 0 or 1
        if free == 'true':
            filters.append('free=1')
        elif free == 'false':
            filters.append('free=0')

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

    details = {
        "details": {
            "page": search_result['page'],
            "number_of_pages": search_result['nbPages'],
            "records_per_page": search_result['hitsPerPage'],
            "total_count": search_result['nbHits'],
        }
    }
    return utils.standardize_response(
        payload=dict(data=results, **details),
        datatype="resources")
