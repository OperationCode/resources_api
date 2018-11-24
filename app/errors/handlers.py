from flask import jsonify
from app.errors import bp
from app import db


# Error Handlers
@bp.app_errorhandler(404)
def page_not_found(e):
    error = {
        "errors": [
            {
                "status": 404,
                "code": "not-found"
            }
        ]
    }
    # Set the 404 status explicitly
    return jsonify(error), 404


@bp.app_errorhandler(500)
def internal_server_error(e):
    error = {
        "errors": [
            {
                "status": 500,
                "code": "internal-server-error"
            }
        ]
    }
    # Set the 500 status explicitly
    return jsonify(error), 500


@bp.teardown_request
def teardown_request(exception=None):
    if exception:
        print('exception', exception)
        db.session.rollback()
    db.session.remove()
