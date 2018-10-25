from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy

bp = Blueprint('api', __name__)
db = SQLAlchemy()