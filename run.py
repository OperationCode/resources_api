from app import cli, create_app, db, search_client, index
from app.models import Category, Language, Resource, db
import os

app = create_app()
cli.register(app, db)

with app.app_context():
    if os.environ.get('INDEX_CHECKED') == "FALSE":
        query = Resource.query
        indicies = search_client.list_indices()
        for ind in indicies['items']:
            if ind['name'] == 'resources_api':
                curr_index = ind
                if curr_index['entries'] != query.all().count():
                    print("ReIndexing Database")
                    db_list = [u.serialize_algolia_search for u in query.all()]
                    index.replace_all_objects(db_list)
                os.environ["INDEX_CHECKED"] = "TRUE"
            break


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Resource': Resource, 'Category': Category, 'Language': Language}
