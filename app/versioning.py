from typing import Callable

import flask

LATEST_API_VERSION = '1.0'
"""latest API version to default to when none other is requested"""


def versioned(function: Callable):
    """
    Extracts requested API version from X-API-Version HTTP header and passes
    to wrapped function in the `version` kwarg.

    :arg function: function to wrap with version parameter
    :returns: wrapped function
    """

    def wrapper(*args, **kwargs):
        version = flask.request.headers.get('x-api-version', LATEST_API_VERSION)
        kwargs['version'] = float(version)
        return function(*args, **kwargs)

    return wrapper
