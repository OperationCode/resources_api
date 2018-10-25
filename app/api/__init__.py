from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy

bp = Blueprint('api', __name__)
db = SQLAlchemy()

# We need to import the routes here so they will
# bind to the blueprint before the blueprint is registered.
from app.api import routes  # noqa
