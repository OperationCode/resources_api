from flask import g, request

from app import db, utils as utils
from app.api import bp
from app.api.auth import authenticate, create_new_apikey, is_user_oc_member, rotate_key
from app.api.routes.helpers import _unauthorized_response
from app.api.routes.logger import logger
from app.api.routes.metrics import failures_counter, latency_summary
from app.api.validations import requires_body
from app.models import Key


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/apikey', methods=['POST'], endpoint='apikey')
@requires_body
def apikey():
    """
    Verify OC membership and return an API key. The API key will be
    saved in the DB to verify use as well as returned upon subsequent calls
    to this endpoint with the same OC credentials.
    """
    json = request.get_json()
    email = json.get('email')
    password = json.get('password')
    is_oc_member = is_user_oc_member(email, password)

    if not is_oc_member:
        return _unauthorized_response()

    try:
        # We need to check the database for an existing key
        apikey = Key.query.filter_by(email=email).first()

        # Don't return success for blacklisted keys
        if apikey and apikey.blacklisted:
            return _unauthorized_response()

        if not apikey:
            # Since they're already authenticated by is_oc_user(), we know we
            # can generate an API key for them if they don't already have one
            apikey = create_new_apikey(email, db.session)
            if not apikey:
                return utils.standardize_response(status_code=500)

        logger.info(apikey.serialize)
        return utils.standardize_response(payload=dict(data=apikey.serialize))
    except Exception as e:
        logger.exception(e)
        return utils.standardize_response(status_code=500)


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/apikey/rotate', methods=['POST'], endpoint='rotate_apikey')
@authenticate
def rotate_apikey():
    new_key = rotate_key(g.auth_key, db.session)
    if not new_key:
        return utils.standardize_response(status_code=500)
    return utils.standardize_response(payload=dict(data=new_key.serialize))
