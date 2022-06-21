from algoliasearch.search_client import SearchClient
from configs import Config
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from healthcheck import HealthCheck
# from healthcheck import EnvironmentDump

from app.versioning import versioned

db = SQLAlchemy()
migrate = Migrate()

# Connect to Agolia
search_client = SearchClient.create(Config.ALGOLIA_APP_ID, Config.ALGOLIA_API_KEY)
index = search_client.init_index(Config.INDEX_NAME)

app = Flask(__name__, static_folder='app/static')

app.config.from_object(Config)
app.url_map.strict_slashes = False

db.init_app(app)
migrate.init_app(app, db)

from app.api import bp as api_bp # noqa
app.register_blueprint(api_bp, url_prefix='/api/v1')

from app.views import bp as view_bp # noqa
app.register_blueprint(view_bp)

from app.errors import bp as error_bp # noqa
app.register_blueprint(error_bp)


@app.route("/healthz")
def healthz():
    health = HealthCheck()
    health.add_section("application", application_data)
    return health.run()


# @app.route("/environment")
# def environment():
#     envdump = EnvironmentDump()
#     envdump.add_section("application", application_data)
#     return envdump.run()


@versioned
def application_data(version):
    return dict(
        apiVersion=version,
        status="ok",
        status_code=200,
        data=None
    )
