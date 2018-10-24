from app import create_app
from app.cli import register
from app.models import Category, Language, Resource, db

app = create_app()
register(app, db)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Resource': Resource, 'Category': Category, 'Language': Language}
