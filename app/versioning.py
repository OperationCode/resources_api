from typing import Callable, List

import flask
from werkzeug.exceptions import HTTPException, BadRequest

VALID_API_VERSIONS = ['1.0']
"""API versions that are valid for a user to request.

NOTE: the first value in this list should be the latest supported version, but the
ordering of subsequent version numbers is not important.
"""
LATEST_API_VERSION = VALID_API_VERSIONS[0]
"""latest API version to default to when none other is requested"""


def versioned(valid_versions: List[str] = None):
    """
    Extracts requested API version from X-API-Version HTTP header and passes
    to wrapped function in the `version` kwarg.

    :arg valid_versions: list of API versions to consider as valid, falls back to
        default list of valid API versions when not specified
    """
    def decorator(function: Callable):
        def wrapper(*args, **kwargs):
            if flask.has_request_context():
                version = flask.request.headers.get('x-api-version', LATEST_API_VERSION)
                if version not in valid_versions:
                    raise InvalidApiVersion(version)
            else:
                version = LATEST_API_VERSION

            kwargs['version'] = float(version)
            return function(*args, **kwargs)

        return wrapper

    # When decorator is not called as a function
    if callable(valid_versions):
        wrapped_function = valid_versions
        valid_versions = VALID_API_VERSIONS
        return decorator(wrapped_function)
    else:
        if not valid_versions:
            valid_versions = VALID_API_VERSIONS
        return decorator


class InvalidApiVersion(BadRequest):
    def __init__(self, version: str):
        super(BadRequest, self).__init__()
        self.description = f'{version} is not a valid API version'
