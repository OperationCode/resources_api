from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask import Flask, url_for, redirect, render_template, request, abort
from app import db
from .models import Resource, Category, Language, User, Role
from flask_security import current_user


class AdminView(ModelView):
    def is_accessible(self):
        return current_user.has_role("admin")
    
    def inaccessible_callback(self):
        return redirect(url_for("security.login", next=request.url))

class HomeAdminView(AdminIndexView):
    def is_accessible(self):
        return current_user.has_role("admin")
    
    def inaccessible_callback(self, name):
        return redirect(url_for("security.login", next=request.url))


def run_flask_admin(app):
    admin = Admin(app, name="Resources_api", url='/', index_view=HomeAdminView(name="Home"))
    admin.add_view(AdminView(Role, db.session))
    admin.add_view(AdminView(User, db.session))
    admin.add_view(AdminView(Resource, db.session))
    admin.add_view(AdminView(Category, db.session))
    admin.add_view(AdminView(Language, db.session))
    return admin

