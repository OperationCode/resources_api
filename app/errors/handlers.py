from app.errors import bp
from app import db
from app.utils import standardize_response


# Error Handlers
@bp.app_errorhandler(400)
def bad_request(e):
    error = dict(
        code="bad-request",
        message=str(e)
    )
    return standardize_response(payload=dict(errors=[error]), status_code=400)


@bp.app_errorhandler(404)
def page_not_found(e):
    return standardize_response(status_code=404)


@bp.app_errorhandler(405)
def method_not_allowed(e):
    return standardize_response(status_code=405)


@bp.app_errorhandler(429)
def ratelimit_handler(e):
    return standardize_response(status_code=429)


@bp.app_errorhandler(500)
def internal_server_error(e):
    return standardize_response(status_code=500)


@bp.teardown_request
def teardown_request(exception=None):
    if exception:
        print('exception', exception)
        db.session.rollback()
    db.session.remove()
