from flask import Blueprint

bp = Blueprint('errors', __name__)

from app.errors import handlers  # noqa

bp.register_error_handler(404, handlers.page_not_found)
bp.register_error_handler(500, handlers.internal_server_error)
