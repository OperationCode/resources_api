from app import create_app, db, cli
from app.models import db, Resource, Category, Language

app = create_app()
cli.register(app, db)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Resource': Resource, 'Category': Category, 'Language': Language}
