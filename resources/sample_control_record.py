import logging
from accessors.celery_task_accessor import CeleryTaskAccessor
from accessors.sample_control_accessor import SampleControlAccessor
from flask_restful import Resource, reqparse
from flask import request
from common.dictionary_helper import DictionaryHelper
from resource_helpers.abort_logger import AbortLogger

parser = reqparse.RequestParser()
# Essential for POST, all other parameters are ignored on post except molecular_id, which, if passed in will cause a
# failure. The proper order is to first POST to get a molecular_id then to PUT the files using the molecular_id in the
# URI. From there other fields can be updated if needed.
parser.add_argument('format',       type=str, required=False)  # format=zip
parser.add_argument('file',         type=str, required=False)  # file=bam|bai|vcf|tsv|all
parser.add_argument('type',         type=str, required=False)  # type=cdna|dna


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
            AbortLogger.log_and_abort(400, self.logger.debug,
                                      "Update item failed, because data to update item with was not passed in request")

        item_dictionary = args.copy()
        item_dictionary.update({'molecular_id': molecular_id})

        # Very important line of code this takes all of the 'None' values out of the dictionary.
        # Without this, the record would update all attributes in the params above with 'None' unless they
        # were explicitly passed in. In reality, we only want to update the attributes that have been explicitly
        # passed in from the params. If they haven't been passed in then they shouldn't be updated.
        item_dictionary = dict((k, v) for k, v in item_dictionary.iteritems() if v)
        try:
            CeleryTaskAccessor().update_item(item_dictionary)
        except Exception as e:
            AbortLogger.log_and_abort(500, self.logger.error, "update_item failed because " + e.message)
        else:
            return {"message": "Sample control with molecular id: " + molecular_id + " updated"}

    def delete(self, molecular_id):
        self.logger.info("Deleting sample control with id: " + str(molecular_id))
        try:
            CeleryTaskAccessor().delete_item({'molecular_id': molecular_id})
        except Exception as e:
            AbortLogger.log_and_abort(500, self.logger.error, "delete_item failed because " + e.message)
        else:
            return {"message": "Item deleted", "molecular_id": molecular_id}

    def get(self, molecular_id):
        self.logger.info("Getting sample control with id: " + str(molecular_id))
        args = request.args
        projection_list, args = DictionaryHelper.get_projection(args)

        try:
            results = SampleControlAccessor().get_item({'molecular_id': molecular_id}, ','.join(projection_list))
        except Exception as e:
            AbortLogger.log_and_abort(500, self.logger.error, "get_item failed because " + e.message)
        else:
            if len(results) > 0:
                self.logger.debug("Found: " + str(results))
                return results

            AbortLogger.log_and_abort(404, self.logger.debug, molecular_id + " was not found")
