import logging
import os
import random
import string
import sys

from .versioning import LATEST_API_VERSION, versioned
from flask import jsonify

err_map = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    422: "Unprocessable Entity",
    429: "Rate Limit Exceeded",
    500: "Server Error"
}

msg_map = {
    400: "Bad Request. Did you provide valid JSON?",
    401: "You must provide a valid API token in the x-apikey header.",
    403: "This endpoint is forbidden.",
    404: "The resource you requested does not exist.",
    405: "This method is not allowed.",
    422: "This request failed validation",
    429: "You have exceeded your rate limit. Try again later.",
    500: "Something went wrong"
}


class Paginator:
    def __init__(self, configuration, request):
        self.configuration = configuration

        self.page = request.args.get('page', 1, type=int)
        self.page_size = request.args.get('page_size', configuration.per_page, type=int)

        if self.page_size > configuration.max_page_size:
            self.page_size = configuration.max_page_size

    def paginated_data(self, query):
        data = query.paginate(self.page, self.page_size, False)
        if self.page > data.pages:
            return None

        setattr(data, "per_page", self.page_size)
        return data

    def pagination_details(self, paginated_data):
        return {
            "pagination_details": {
                "page": paginated_data.page,
                "number_of_pages": paginated_data.pages,
                "records_per_page": paginated_data.per_page,
                "total_count": paginated_data.total,
                "has_next": paginated_data.has_next,
                "has_prev": paginated_data.has_prev
            }
        }


def format_resource_search(hit):
    formatted = {
        'id': hit['id'],
        'name': hit['name'],
        'url': hit['url'],
        'category': hit['category'],
        'languages': hit['languages'],
        'paid': hit['paid'],
        'notes': hit['notes'],
        'upvotes': hit['upvotes'],
        'downvotes': hit['downvotes'],
        'times_clicked': hit['times_clicked'],
        'created_at': hit['created_at'],
        'last_updated': hit['last_updated'],
    }

    return formatted


@versioned(throw_on_invalid=False)
def standardize_response(payload={}, status_code=200, version=LATEST_API_VERSION):
    """Response helper
    This simplifies the response creation process by providing an internally
    defined mapping of status codes to messages for errors. It also knows when
    to respond with a server error versus when to be 'ok' based on the keys
    present in the supplied payload.
    If the payload has falsey data and no error key defined, it responds with
    a 500.
    Arguments:
    payload -- None or a dict with 'data' or 'error' keys, 'data' should be
    json serializable
    status_code -- a valid HTTP status code. For errors it defaults to 500,
    for 'ok' it defaults to 200
    """
    data = payload.get("data")
    errors = payload.get("errors")
    pagination_details = payload.get("pagination_details")
    resp = dict(
        apiVersion=version,
        status="ok",
        status_code=status_code,
        data=None
    )

    if status_code >= 400 and err_map.get(status_code):
        resp["status"] = err_map.get(status_code)
        resp["status_code"] = status_code

        if errors:
            resp["errors"] = errors
        else:
            code = get_error_code_from_status(status_code)
            message = msg_map.get(status_code)
            resp["errors"] = {}
            resp["errors"][code] = {"message": message}

    elif not data:
        # 500 Error case -- Something went wrong.
        message = msg_map.get(500)
        resp["errors"] = {'errors': {"server-error": {"message": message}}}
        resp["status_code"] = 500
        resp["status"] = err_map.get(500)
    else:
        resp["data"] = data

        if pagination_details:
            resp.update(pagination_details)

    return jsonify(resp), resp["status_code"], {'Content-Type': 'application/json'}


def setup_logger(name, level=logging.INFO):
    """Function setup as many loggers as you want"""
    if not os.path.exists('log'):
        os.makedirs('log')  # pragma: no cover

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def get_error_code_from_status(status_code):
    return '-'.join(err_map.get(status_code).split(' ')).lower()


def random_string(n=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))
