from app import app, cli
from app.models import Category, Language, Resource, db
from werkzeug.serving import run_simple

if __name__ == "__main__":
    run_simple(hostname='0.0.0.0', port=5000, application=app,
               use_reloader=True, use_debugger=True, use_evalex=True)

cli.register(app, db)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Resource': Resource, 'Category': Category, 'Language': Language}
