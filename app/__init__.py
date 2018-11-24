from sys import version_info

from configs import Config
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

try:
    assert version_info >= (3, 7, 0)
except AssertionError:
    print('Warning Current Python version not supported')
    print('Current Python version: {version}'.format(version=version_info))
    exit(1)


db = SQLAlchemy()
migrate = Migrate()

API_VERSION = "1.0"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    from app.errors import bp as error_bp
    app.register_blueprint(error_bp)

    return app
