from os import environ

from algoliasearch.exceptions import AlgoliaException, AlgoliaUnreachableHostException
from flask import redirect, request
from sqlalchemy.exc import IntegrityError

from app import db, index, utils as utils
from app.api import bp
from app.api.auth import authenticate
from app.api.routes.helpers import (
    failures_counter, get_attributes, latency_summary, logger)
from app.api.validations import requires_body, validate_resource, wrong_type
from app.models import Resource


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/resources/<int:id>', methods=['PUT'], endpoint='update_resource')
@requires_body
@authenticate
def put_resource(id):
    json = request.get_json()

    if not isinstance(json, dict):
        return wrong_type("resource object", type(json))

    validation_errors = validate_resource(request.method, json, id)

    if validation_errors:
        errors = {"errors": validation_errors}
        return utils.standardize_response(payload=errors, status_code=422)
    return update_resource(id, request.get_json(), db)


def update_resource(id, json, db):
    resource = Resource.query.get(id)

    if not resource:
        return redirect('/404')

    langs, categ = get_attributes(json)
    index_object = {'objectID': id}

    try:
        logger.info(f"Updating resource. Old data: {resource.serialize}")
        if json.get('languages'):
            resource.languages = langs
            index_object['languages'] = resource.serialize['languages']
        if json.get('category'):
            resource.category = categ
            index_object['category'] = categ.name
        if json.get('name'):
            resource.name = json.get('name')
            index_object['name'] = json.get('name')
        if json.get('url'):
            resource.url = json.get('url')
            index_object['url'] = json.get('url')
        if 'paid' in json:
            paid = json.get('paid')

            # Converts "false" and "true" to their bool
            if type(paid) is str and paid.lower() in ["true", "false"]:
                paid = paid.lower().strip() == "true"
            resource.paid = paid
            index_object['paid'] = paid
        if 'notes' in json:
            resource.notes = json.get('notes')
            index_object['notes'] = json.get('notes')

        try:
            index.partial_update_object(index_object)

        except (AlgoliaUnreachableHostException, AlgoliaException) as e:
            if environ.get("FLASK_ENV") != 'development':
                logger.exception(e)
                msg = f"Algolia failed to update index for resource '{resource.name}'"
                logger.warn(msg)
                error = {'errors': [{"algolia-failed": {"message": msg}}]}
                return utils.standardize_response(payload=error, status_code=500)

        # Wait to commit the changes until we know that Aloglia was updated
        db.session.commit()

        return utils.standardize_response(
            payload=dict(data=resource.serialize)
        )

    except IntegrityError as e:
        logger.exception(e)
        return utils.standardize_response(status_code=422)

    except Exception as e:
        logger.exception(e)
        return utils.standardize_response(status_code=500)


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
