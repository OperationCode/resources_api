from flask import request
from app.models import Resource
from app.utils import standardize_response


def requires_body(func):
    def wrapper(*args, **kwargs):
        try:
            # JSON body is {}
            if not request.get_json():
                return missing_json_error()
        except Exception as e:
            # JSON body is completely missing
            if "Expecting value: line 1 column 1" in str(e):
                return missing_json_error()

        return func(*args, **kwargs)
    return wrapper


def missing_json_error():
    message = "You must provide a valid JSON body to use this endpoint"
    error = {'errors': {"missing-body": {"message": message}}}
    return standardize_response(error, status_code=422)


def validate_resource(request, id=-1):
    errors = None
    json = request.get_json()
    validation_errors = {"errors": {}}
    missing_params = {"params": []}
    invalid_params = {"params": []}
    required = []

    for column in Resource.__table__.columns:
        # strip _id from category_id
        col_name = column.name.replace('_id', '')

        # There are only required parameters for POSTing new resources.
        if request.method == 'POST':
            if column.nullable is False and col_name != 'id':
                required.append(col_name)

        # Type Validation.
        col_type = column.type.python_type
        field = json.get(col_name)

        if field is not None:

            # Category is a foreign key (int) relation but we only accept string input.
            # The provided category will get mapped to this resource later on.
            if col_name == 'category':
                col_type = str

            # Allow String columns to accept integers.
            if col_type is str:
                if type(field) in [int, float]:

                    # Do not allow integers as urls
                    if col_name != 'url':
                        continue

            # Allow Bool columns to accept strings that are variations "true" or "false"
            if col_type is bool:
                if type(field) is str and field.lower() in ["false", "true"]:
                    continue

            # Validate that fields are of the correct type.
            if col_type is not type(field):
                invalid_params["params"].append(col_name)

    # Special case for Languages - Must be list and all elements must be str.
    langs = json.get('languages')
    if langs:
        if type(langs) is not list or not all(map(lambda x: type(x) is str, langs)):
            invalid_params["params"].append("languages")

    for prop in required:
        if json.get(prop) is None:
            missing_params["params"].append(prop)

    url = json.get("url")
    if url is not None:

        # If there is an existing resource with the requested url
        # and it isn't the Resource we are trying to update, return an error.
        resource = Resource.query.filter_by(url=url).first()
        if resource and resource.id != id:
            invalid_params["params"].append('url')
            message = f"Resource id {resource.id} already has this URL."
            invalid_params["message"] = message
            invalid_params["resource"] = \
                f"https://resources.operationcode.org/api/v1/{resource.id}"

    if missing_params["params"]:
        validation_errors["errors"]["missing-params"] = missing_params
        msg = " The following params were missing: "
        msg += ", ".join(missing_params.get("params")) + "."
        validation_errors["errors"]["missing-params"]["message"] = msg
        errors = True

    if invalid_params["params"]:
        validation_errors["errors"]["invalid-params"] = invalid_params
        msg = " The following params were invalid: "
        msg += ", ".join(invalid_params.get("params")) + ". "
        msg += invalid_params.get("message", "")
        validation_errors["errors"]["invalid-params"]["message"] = msg.strip()
        errors = True

    if errors:
        return validation_errors
