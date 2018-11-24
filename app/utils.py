from app import API_VERSION
from flask import jsonify


class Paginator:
    def __init__(self, configuration, request):
        self.configuration = configuration

        self.page = request.args.get('page', 1, type=int)
        self.page_size = request.args.get('page_size', configuration.per_page, type=int)

        if self.page_size > configuration.max_page_size:
            self.page_size = configuration.max_page_size

    def items(self, query):
        return query.paginate(self.page, self.page_size, False).items


def standardize_response(data, errors, status):
    resp = {
        "status": status,
        "apiVersion": API_VERSION
    }
    if data:
        resp["data"] = data
    elif errors:
        resp["errors"] = errors
    else:
        resp["errors"] = [{"code": "something-went-wrong"}]
    return jsonify(resp)
