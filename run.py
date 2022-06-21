from app import app, cli
from app.admin import run_flask_admin
from app.models import Category, Language, Resource, db, Role, User
import os
from flask_security import Security, SQLAlchemyUserDatastore, utils
from flask import url_for
from flask_admin import helpers as admin_helpers
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
from sqlalchemy import event

admin = run_flask_admin(app)

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

if __name__ == "__main__":
    app.run()

cli.register(app, db)

# Add prometheus wsgi middleware to route /metrics requests
app_dispatch = DispatcherMiddleware(app, {
    '/metrics': make_wsgi_app()
})


# @event.listens_for(User.password, 'set', retval=True)
# def hash_user_password(target, value, oldvalue, initiator):
#     """Encrypts password when new admin created in User View"""
#     if value != oldvalue:
#         return utils.encrypt_password(value)
#     return value


@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Resource': Resource, 'Category': Category, 'Language': Language,
            'User': User, 'Role': Role}


@app.before_first_request
def before_first_request():
    """ Adds admin/user roles and default admin account and password if none exists"""
    db.create_all()
    user_datastore.find_or_create_role(name='admin', description='Administrator')
    user_datastore.find_or_create_role(name='user', description='End User')

    admin_email = os.environ.get('ADMIN_EMAIL', "admin@example.com")
    admin_password = os.environ.get('ADMIN_PASSWORD', 'password')

    encrypted_password = utils.encrypt_password(admin_password)

    if not user_datastore.get_user(admin_email):
        user_datastore.create_user(email=admin_email, password=encrypted_password)
        db.session.commit()

    user_datastore.add_role_to_user(admin_email, 'admin')
    db.session.commit()


if __name__ == "__main__":
    app.run()
