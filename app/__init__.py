from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sys import version_info

try:
    assert version_info >= (3,7,0)
except AssertionError as e:
    print('Warning Current python version not supported')
    print('Current python version: {version}'.format(version=version_info))
    exit(1)
    
from configs import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    return app
