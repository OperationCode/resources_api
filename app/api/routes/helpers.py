from app import utils as utils


def _unauthorized_response():
    message = "The email or password you submitted is incorrect " \
              "or your account is not allowed api access"
    payload = {'errors': {"invalid-credentials": {"message": message}}}
    return utils.standardize_response(payload=payload, status_code=401)
