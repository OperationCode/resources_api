from flask import Blueprint
from flask_cors import CORS

bp = Blueprint('api', __name__)

ALLOWED_ORIGINS = [
    'http://localhost:3000',
    r"https:\/\/(www\.)?operationcode\.org",
    r"https:\/\/(.*\.)?operation-code(-.*)?\.now\.sh",
    r"https:\/\/(.*\.)?operation-code(-.*)?\.vercel\.app"
]

CORS(bp, origins=ALLOWED_ORIGINS)

# We need to import the routes here so they will
# bind to the blueprint before the blueprint is registered.
from app.api import routes  # noqa
