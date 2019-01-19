from app import API_VERSION
from flask import jsonify
import logging
import os


class Paginator:
    def __init__(self, configuration, request):
        self.configuration = configuration

        self.page = request.args.get('page', 1, type=int)
        self.page_size = request.args.get('page_size', configuration.per_page, type=int)

        if self.page_size > configuration.max_page_size:
            self.page_size = configuration.max_page_size

    def items(self, query):
        return query.paginate(self.page, self.page_size, False).items


def standardize_response(data, errors, status, status_code=200):
    resp = {
        "status": status,
        "apiVersion": API_VERSION
    }
    if data is not None:
        resp["data"] = data
    elif errors:
        resp["errors"] = errors
    else:
        resp["errors"] = [{"code": "something-went-wrong"}]
    return jsonify(resp), status_code


def setup_logger(name, log_file, level=logging.INFO):
    """Function setup as many loggers as you want"""
    if not os.path.exists('log'):
        os.makedirs('log')

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
