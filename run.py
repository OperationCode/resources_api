from app import app, cli, admin
from app.models import Category, Language, Resource, db, User, Role
from flask_security import Security, SQLAlchemyUserDatastore
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app


admin.run_flask_admin(app)

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

if __name__ == "__main__":
    app.run()

cli.register(app, db)

# Add prometheus wsgi middleware to route /metrics requests
app_dispatch = DispatcherMiddleware(app, {
    '/metrics': make_wsgi_app()
})


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Resource': Resource, 'Category': Category, 'Language': Language}
