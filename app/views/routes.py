from os.path import join

from flask import send_from_directory, current_app, render_template

from app.views import bp


@bp.route('/', methods=['GET'])
def docs():
    """ Displays the API documentation at '/'
    """
    return render_template('index.html')


@bp.route('/favicon.ico', methods=['GET'])
def favicon():
    return send_from_directory(join(current_app.root_path, 'static'), 'favicon.ico')


