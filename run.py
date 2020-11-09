from app import app, cli, admin
import os
from app.models import Category, Language, Resource, db, User, Role
from flask_security import Security, SQLAlchemyUserDatastore, utils
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
    return {'db': db, 'Resource': Resource, 'Category': Category,
            'Language': Language, 'User': User, 'Role': Role}


# Create Admin user and role.
@app.before_first_request
def before_first_request():
    # Create any database tables that don't exist yet.
    db.create_all()

    # Create the Roles "admin" and "user" -- unless they already exist
    user_datastore.find_or_create_role(name='admin', description='Administrator')
    user_datastore.find_or_create_role(name='user', description='End user')

    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'password')

    # Create two Users for testing purposes -- unless they already exists.
    # In each case, use Flask-Security utility function to encrypt the password.
    encrypted_password = utils.encrypt_password(admin_password)
    if not user_datastore.get_user(admin_email):
        user_datastore.create_user(email=admin_email,
                                   password=encrypted_password)
    # Add more users.

    # Commit any database changes; the User and Roles must exist before we
    # can add a Role to the User
    db.session.commit()

    # Give one User has the "end-user" role, while the other has the "admin"
    # role. (This will have no effect if the
    # Users already have these Roles.) Again, commit any database changes.
    user_datastore.add_role_to_user(admin_email, 'admin')
    db.session.commit()
