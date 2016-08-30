import logging
from accessors.celery_task_accessor import CeleryTaskAccessor
from accessors.sample_control_accessor import SampleControlAccessor
from flask_restful import abort, reqparse, Resource
from flask import request
from common.dictionary_helper import DictionaryHelper


class SampleControlRecord(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # this put should just put items on the queue through celery and then let celery update
    # the database, shouldn't process files (molecular_id resource does that).
    # This is just straight updates of attributes.
    def put(self, molecular_id):
        self.logger.info("updating sample control with id: " + str(molecular_id))
        args = request.json
        self.logger.debug(str(args))

        if not DictionaryHelper.has_values(args):
            self.logger.debug("Update item failed, because data to update item with was not passed in request")
            abort(400, message="Update item failed, because data to update item with was not passed in request")

        item_dictionary = args.copy()
        item_dictionary.update({'molecular_id': molecular_id})

        # Very important line of code this takes all of the 'None' values out of the dictionary.
        # Without this, the record would update all attributes in the params above with 'None' unless they
        # were explicitly passed in. In reality, we only want to update the attributes that have been explicitly
        # passed in from the params. If they haven't been passed in then they shouldn't be updated.
        item_dictionary = dict((k, v) for k, v in item_dictionary.iteritems() if v)
        try:
            CeleryTaskAccessor().update_item(item_dictionary)
        except Exception, e:
            self.logger.debug("updated_item failed because " + e.message)
            abort(500, message="Update item failed, because " + e.message)

        return {"message": "Sample control with molecular id: " + molecular_id + " updated"}

    def delete(self, molecular_id):
        self.logger.info("Deleting sample control with id: " + str(molecular_id))
        try:
            CeleryTaskAccessor().delete_item({'molecular_id': molecular_id})
            return {"message": "Item deleted", "molecular_id": molecular_id}
        except Exception, e:
            self.logger.debug("delete_item failed because" + e.message)
            abort(500, message="delete_item item failed, because " + e.message)

    # TODO: Expand GET functionality to include the retrieval of files from S3.
    # see https://wiki.nci.nih.gov/display/UM/Ecosystems+Services+and+Tables for more information on the functionality
    # that is needed to be added
    def get(self, molecular_id):
        self.logger.info("Getting sample control with id: " + str(molecular_id))
        try:
            results = SampleControlAccessor().get_item({'molecular_id': molecular_id})

            if 'Item' in results:
                self.logger.debug("Found: " + str(results['Item']))
                return results['Item']

        except Exception, e:
            self.logger.debug("get_item failed because" + e.message)
            abort(500, message="get_item failed because " + e.message)

        self.logger.info(molecular_id + " was not found")
        abort(404, message=str(molecular_id + " was not found"))
