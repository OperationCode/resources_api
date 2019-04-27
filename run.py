from app import cli, create_app, db, API_VERSION
from app.models import Category, Language, Resource, db
from werkzeug.wsgi import DispatcherMiddleware
from prometheus_client import make_wsgi_app
import json

app = create_app()
cli.register(app, db)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Resource': Resource, 'Category': Category, 'Language': Language}


def make_health_endpoint():
    """Create a WSGI app which serves as a heartbeat"""

    def app(environ, start_response):
        status = str('200 OK')
        headers = [(str('Content-type'), 'application/json')]
        response_body = json.dumps(dict(
            apiVersion=API_VERSION,
            status="ok",
            status_code=200,
            data=None
        )).encode()
        start_response(status, headers)
        return [response_body]

    return app


# Add prometheus wsgi middleware to route /metrics requests
# TODO: healthz should conform to https://inadarei.github.io/rfc-healthcheck/
app_dispatch = DispatcherMiddleware(app, {
    '/metrics': make_wsgi_app(),
    '/healthz': make_health_endpoint()
})
