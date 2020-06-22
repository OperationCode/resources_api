from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from app import db, app
from .models import Resource, Category, Language


def run_flask_admin():
    admin = Admin(app)
    admin.add_view(ModelView(Resource, db.session))
    admin.add_view(ModelView(Category, db.session))
    admin.add_view(ModelView(Language, db.session))

# end
