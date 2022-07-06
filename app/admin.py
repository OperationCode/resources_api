from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask import url_for, redirect, request, abort
from app import db
from .models import Resource, Category, Language, User, Role
from flask_security import current_user


class AdminView(ModelView):
    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and current_user.has_role('admin'))

    def _handle_view(self, name, **kwargs):
        """ Override builtin _handle_view in order to redirect users when a view
        is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


class HomeAdminView(AdminIndexView):
    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name):
        return redirect(url_for('security.login', next=request.url))


def run_flask_admin(app):
    """Creates the admin object and defines which views will be visible"""
    admin_obj = Admin(app, name='Resources_api', url='/',
                      base_template='my_master.html',
                      index_view=HomeAdminView(name='Home'))
    admin_obj.add_view(AdminView(Role, db.session))
    admin_obj.add_view(AdminView(User, db.session))
    admin_obj.add_view(AdminView(Resource, db.session))
    admin_obj.add_view(AdminView(Category, db.session))
    admin_obj.add_view(AdminView(Language, db.session))
    return admin_obj
