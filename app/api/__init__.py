from flask import Blueprint

bp = Blueprint('api', __name__)

# We need to import the routes here so they will bind to the blueprint before the blueprint is registered.
from app.api import routes  # noqa
