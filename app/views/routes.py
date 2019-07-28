from os.path import join

from flask import send_from_directory, current_app, render_template

from app.views import bp

import os


@bp.route('/', methods=['GET'])
def docs():
    """
    Displays the API documentation at '/'
    """
    return render_template('index.html',
                           last_updated=dir_last_updated('app/static'))


@bp.route('/openapi.yaml', methods=['GET'])
def open_api_yaml():
    """
    Serves up the openapi.yaml file
    """
    return send_from_directory(join(current_app.root_path, 'static'), 'openapi.yaml')


@bp.route('/favicon.ico', methods=['GET'])
def favicon():
    """
    Serves the favicon
    """
    return send_from_directory(join(current_app.root_path, 'static'), 'favicon.ico')


def dir_last_updated(folder):
    """
    Returns the timestamp of the last time the static folder was updated
    to avoid the browser caching an outdated openapi.yaml file
    """
    return str(max(os.path.getmtime(os.path.join(root_path, f))
               for root_path, dirs, files in os.walk(folder)
               for f in files))
