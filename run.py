from app import cli, create_app, db
from app.models import Category, Language, Resource, db

app = create_app()
cli.register(app, db)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Resource': Resource, 'Category': Category, 'Language': Language}
