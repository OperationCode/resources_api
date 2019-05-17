
from app import cli, create_app, db, search_client, index
from app.models import Category, Language, Resource, db
from werkzeug.wsgi import DispatcherMiddleware
from prometheus_client import make_wsgi_app
import os


app = create_app()
cli.register(app, db)

# Add prometheus wsgi middleware to route /metrics requests
app_dispatch = DispatcherMiddleware(app, {
    '/metrics': make_wsgi_app()
})

with app.app_context():
    if os.environ.get('INDEX_SEARCHED') == "FALSE":
        query = Resource.query
        indicies = search_client.list_indices()
        for ind in indicies['items']:
            if ind['name'] == os.environ.get('INDEX_NAME'):
                curr_index = ind

                if curr_index['entries'] != query.count():
                    db_list = [u.serialize_algolia_search for u in query.all()]
                    index.replace_all_objects(db_list)

                os.environ["INDEX_SEARCHED"] = "TRUE"
                break


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Resource': Resource, 'Category': Category, 'Language': Language}
