from app import current_app
from flask import jsonify
import json
import traceback
from app.models import Resource, Category, Language

with app.context():
    @app.route('/resources', methods=['GET'])
    def resources():
        return get_resources()

    def get_resources():
        resources = {}
        try:
            resources = Resource.query.all()
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            print(e)

        return jsonify([single_resource.serialize for single_resource in resources])