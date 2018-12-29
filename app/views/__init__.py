from flask import Blueprint

bp = Blueprint('views', __name__)

# We need to import the routes here so they will
# bind to the blueprint before the blueprint is registered.
from app.views import routes  # noqa
