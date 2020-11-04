from os import environ

from algoliasearch.exceptions import AlgoliaException, AlgoliaUnreachableHostException
from flask import request
from sqlalchemy.exc import IntegrityError

from app import db, index, utils as utils
from app.api import bp
from app.api.auth import authenticate
from app.api.routes.helpers import (
    failures_counter, get_attributes, latency_summary, logger, ensure_bool)
from app.api.validations import requires_body, validate_resource_list, wrong_type
from app.models import Resource


@latency_summary.time()
@failures_counter.count_exceptions()
@bp.route('/resources', methods=['POST'], endpoint='create_resources')
@requires_body
@authenticate
def post_resources():
    json = request.get_json()

    if not isinstance(json, list):
        return wrong_type("list of resources objects", type(json))

    validation_errors = validate_resource_list(request.method, json)

    if validation_errors:
        return utils.standardize_response(payload=validation_errors, status_code=422)

    return create_resources(json, db)


def create_resources(json, db):
    try:
        # Resources to return in the response
        created_resources = []
        # Serialized Resources to send to Algolia
        created_resources_algolia = []
        # Resource IDs to delete if Algolia fails to index
        resource_id_cache = []

        # Create each Resource in the database one by one
        for resource in json:
            langs, categ = get_attributes(resource)
            free_bool = ensure_bool(resource.get('free'))
            new_resource = Resource(
                name=resource.get('name'),
                url=resource.get('url'),
                category=categ,
                languages=langs,
                free=free_bool,
                notes=resource.get('notes'))

            try:
                db.session.add(new_resource)
                db.session.commit()
                created_resources_algolia.append(new_resource.serialize_algolia_search)
                resource_id_cache.append(new_resource.id)

            except IntegrityError as e:
                logger.exception(e)
                return utils.standardize_response(status_code=422)

            except Exception as e:
                logger.exception(e)
                return utils.standardize_response(status_code=500)

            created_resources.append(new_resource.serialize())

        # Take all the created resources and save them in Algolia with one API call
        try:
            index.save_objects(created_resources_algolia)

        except (AlgoliaUnreachableHostException, AlgoliaException) as e:
            if (environ.get("FLASK_ENV") != 'development'):
                logger.exception(e)

                # Remove created resources from the db to stay in sync with Algolia
                for res_id in resource_id_cache:
                    res = Resource.query.get(res_id)
                    res.languages.clear()
                    db.session.delete(res)
                db.session.commit()

                msg = "Algolia failed to index resources"
                error = {'errors': [{"algolia-failed": {"message": msg}}]}
                return utils.standardize_response(payload=error, status_code=500)

        # Success
        return utils.standardize_response(
            payload=dict(data=created_resources),
            datatype="resources")
    except Exception as e:
        logger.exception(e)
        return utils.standardize_response(status_code=500)
