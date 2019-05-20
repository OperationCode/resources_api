from algoliasearch.search_client import SearchClient
from configs import Config
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
migrate = Migrate()

API_VERSION = "1.0"

# healthcheck uses API_VERSION so this has to come after it's declared
from app.healthcheck import add_health_check # noqa

# Connect to Agolia
search_client = SearchClient.create(Config.SEARCH_ID, Config.SEARCH_KEY)
index = search_client.init_index(Config.INDEX_NAME)

def create_app(config_class=Config):
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_class)
    app.url_map.strict_slashes = False

    Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )

    db.init_app(app)
    migrate.init_app(app, db)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    from app.views import bp as view_bp
    app.register_blueprint(view_bp)

    from app.errors import bp as error_bp
    app.register_blueprint(error_bp)

    add_health_check(app)

    return app
