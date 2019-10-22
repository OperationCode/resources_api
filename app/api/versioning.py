from typing import Callable

import flask

DEFAULT_VERSION = '1.0'
"""default API version to utilize when none other is requested"""


def versioned(function: Callable):
    """
    Extracts requested API version from X-API-Version HTTP header and passes
    to wrapped function in the `version` kwarg.

    :arg function: function to wrap with version parameter
    :returns: wrapped function
    """

    def wrapper(*args, **kwargs):
        version = flask.request.headers.get('x-api-version', DEFAULT_VERSION)
        kwargs['version'] = float(version)
        return function(*args, **kwargs)

    return wrapper
