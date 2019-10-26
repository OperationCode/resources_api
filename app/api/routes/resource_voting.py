from werkzeug.utils import redirect

from app import db, utils as utils
from app.api import bp
from app.api.routes.utils import latency_summary, failures_counter
from app.models import Resource


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/resources/<int:id>/upvote', methods=['PUT'])
def upvote(id):
    return update_votes(id, 'upvotes')


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/resources/<int:id>/downvote', methods=['PUT'])
def downvote(id):
    return update_votes(id, 'downvotes')


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/resources/<int:id>/click', methods=['PUT'])
def update_resource_click(id):
    return add_click(id)


def update_votes(id, vote_direction):
    resource = Resource.query.get(id)

    if not resource:
        return redirect('/404')

    initial_count = getattr(resource, vote_direction)
    setattr(resource, vote_direction, initial_count + 1)
    db.session.commit()

    return utils.standardize_response(payload=dict(data=resource.serialize))


def add_click(id):
    resource = Resource.query.get(id)

    if not resource:
        return redirect('/404')

    initial_count = getattr(resource, 'times_clicked')
    setattr(resource, 'times_clicked', initial_count + 1)
    db.session.commit()

    return utils.standardize_response(payload=dict(data=resource.serialize))
