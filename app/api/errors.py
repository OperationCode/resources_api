from flask import jsonify


# Error Handlers
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
