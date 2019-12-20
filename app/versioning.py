from typing import Callable, Iterable

import flask
from werkzeug.exceptions import BadRequest

VALID_API_VERSIONS = ('1.0',)
"""API versions that are valid for a user to request.

NOTE: the first value in this list should be the latest supported version, but the
ordering of subsequent version numbers is not important.
"""
LATEST_API_VERSION = VALID_API_VERSIONS[0]
"""latest API version to default to when none other is requested"""


def versioned(
        valid_versions: Iterable[str] = VALID_API_VERSIONS,
        throw_on_invalid: bool = True):
    """
    Extracts requested API version from X-API-Version HTTP header and passes
    to wrapped function in the `version` kwarg.

    :param throw_on_invalid: whether to throw exception on invalid passed version,
        defaults to `True`
    :param valid_versions: list of API versions to consider as valid, falls back to
        default list of valid API versions when not specified
    :raise InvalidApiVersion: when `throw_on_invalid` is `True` and invalid API version
        was specified in the client request
    """

    def decorator(function: Callable):
        def wrapper(*args, **kwargs):
            if flask.has_request_context():
                version = flask.request.headers.get('x-api-version', LATEST_API_VERSION)
                if version not in valid_versions:
                    if throw_on_invalid:
                        raise InvalidApiVersion(version)
                    else:
                        version = LATEST_API_VERSION
            else:
                version = LATEST_API_VERSION

            kwargs['version'] = version
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
    """An invalid API version was requested in the inbound HTTP request."""

    def __init__(self, invalid_version: str):
        super(BadRequest, self).__init__()
        self.description = f'{invalid_version} is not a valid API version'
