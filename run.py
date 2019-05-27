from app import cli, create_app
from app.models import Category, Language, Resource, db
from werkzeug.wsgi import DispatcherMiddleware
from prometheus_client import make_wsgi_app

app = create_app()
cli.register(app, db)

# Add prometheus wsgi middleware to route /metrics requests
app_dispatch = DispatcherMiddleware(app, {
    '/metrics': make_wsgi_app()
})


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Resource': Resource, 'Category': Category, 'Language': Language}
