import logging
from flask_restful import abort, request, Resource, reqparse
from accessors.celery_task_accessor import CeleryTaskAccessor
from accessors.ion_reporter_accessor import IonReporterAccessor
from common.dictionary_helper import DictionaryHelper

parser = reqparse.RequestParser()

parser.add_argument('projection',       type=str, required=False)


class IonReporterRecord(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get(self, ion_reporter_id):
        self.logger.info("Getting ion reporter with id: " + str(ion_reporter_id))
        args = parser.parse_args()

        try:
            results = IonReporterAccessor().get_item({'ion_reporter_id': ion_reporter_id})
        except Exception, e:
            self.logger.debug("Major server error!!!")
            abort(500, message="Server error " + e.message)
        else:
            if len(results) < 1:
                self.logger.debug("Ion Reporter with id: " + str(ion_reporter_id) +
                                  " was not found in ion reporter table")
                abort(404, message="Ion Reporter with id: " + str(ion_reporter_id) +
                                   " was not found in ion reporter table")

            return results

    def put(self, ion_reporter_id):
        self.logger.info("updating ion reporter with id: " + str(ion_reporter_id))
        args = request.json
        self.logger.debug(str(args))

        if not DictionaryHelper.has_values(args):
            self.logger.debug("Update item failed, because data to update item with was not passed in request")
            abort(400, message="Update item failed, because data to update item with was not passed in request")

        item_dictionary = args.copy()
        item_dictionary.update({'ion_reporter_id': ion_reporter_id})

        # Very important line of code this takes all of the 'None' values out of the dictionary.
        # Without this, the record would update all attributes in the params above with 'None' unless they
        # were explicitly passed in. In reality, we only want to update the attributes that have been explicitly
        # passed in from the params. If they haven't been passed in then they shouldn't be updated.
        item_dictionary = dict((k, v) for k, v in item_dictionary.iteritems() if v)
        try:
            CeleryTaskAccessor().update_ir_item(item_dictionary)
            # IonReporterAccessor().update(item_dictionary)
        except Exception, e:
            self.logger.debug("updated_item failed because" + e.message)
            abort(500, message="Update item failed, because " + e.message)

        return {"message": "Ion reporter with ion reporter id: " + ion_reporter_id + " updated"}

    def delete(self, ion_reporter_id):
        self.logger.info("Deleting ion reporter with id: " + str(ion_reporter_id))
        try:
            CeleryTaskAccessor().delete_ir_item({'ion_reporter_id': ion_reporter_id})
            return {"message": "Item deleted", "ion_reporter_id": ion_reporter_id}
        except Exception, e:
            self.logger.debug("delete_item failed because" + e.message)
            abort(500, message="delete_item item failed, because " + e.message)