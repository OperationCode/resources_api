from flask import Flask
from flask_migrate import Migrate
from configs import Config

from .models import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    migrate = Migrate(app, db)
    return app
