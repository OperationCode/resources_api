from algoliasearch.exceptions import AlgoliaException, AlgoliaUnreachableHostException
from flask import redirect, request
from sqlalchemy.exc import IntegrityError

from app import db, index, utils as utils
from app.api import bp
from app.api.auth import authenticate
from app.api.routes.utils import (
    failures_counter, get_attributes, latency_summary, logger)
from app.api.validations import requires_body, validate_resource
from app.models import Resource


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/resources', methods=['POST'], endpoint='create_resource')
@requires_body
@authenticate
def post_resources():
    validation_errors = validate_resource(request)

    if validation_errors:
        return utils.standardize_response(payload=validation_errors, status_code=422)
    return create_resource(request.get_json(), db)


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/resources/<int:id>', methods=['PUT'], endpoint='update_resource')
@requires_body
@authenticate
def put_resource(id):
    validation_errors = validate_resource(request, id)

    if validation_errors:
        return utils.standardize_response(payload=validation_errors, status_code=422)
    return update_resource(id, request.get_json(), db)


def create_resource(json, db):
    langs, categ = get_attributes(json)
    new_resource = Resource(
        name=json.get('name'),
        url=json.get('url'),
        category=categ,
        languages=langs,
        paid=json.get('paid'),
        notes=json.get('notes'))

    try:
        db.session.add(new_resource)
        db.session.commit()
        index.save_object(new_resource.serialize_algolia_search)

    except (AlgoliaUnreachableHostException, AlgoliaException) as e:
        logger.exception(e)
        print(f"Algolia failed to index new resource '{new_resource.name}'")

    except IntegrityError as e:
        logger.exception(e)
        return utils.standardize_response(status_code=422)

    except Exception as e:
        logger.exception(e)
        return utils.standardize_response(status_code=500)

    return utils.standardize_response(payload=dict(data=new_resource.serialize))


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

        db.session.commit()

        try:
            index.partial_update_object(index_object)

        except (AlgoliaUnreachableHostException, AlgoliaException) as e:
            logger.exception(e)
            print(f"Algolia failed to update index for resource '{resource.name}'")

        return utils.standardize_response(
            payload=dict(data=resource.serialize)
        )

    except IntegrityError as e:
        logger.exception(e)
        return utils.standardize_response(status_code=422)

    except Exception as e:
        logger.exception(e)
        return utils.standardize_response(status_code=500)
