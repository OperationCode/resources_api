from app.errors import bp
from app import db
from app.utils import standardize_response


# Error Handlers
@bp.app_errorhandler(404)
def page_not_found(e):
    errors = [
        {
            "status": 404,
            "code": "not-found"
        }
    ]

    # Set the 404 status explicitly
    return standardize_response(None, errors, "not found", 404)


@bp.app_errorhandler(429)
def ratelimit_handler(e):
    errors = [
        {
            "status": 429,
            "code": "rate-limit-exceeded"
        }
    ]

    return standardize_response(None, errors, e.description, 429)


@bp.app_errorhandler(500)
def internal_server_error(e):
    errors = [
        {
            "status": 500,
            "code": "internal-server-error"
        }
    ]

    # Set the 500 status explicitly
    return standardize_response(None, errors, "internal server error", 500)


@bp.teardown_request
def teardown_request(exception=None):
    if exception:
        print('exception', exception)
        db.session.rollback()
    db.session.remove()
