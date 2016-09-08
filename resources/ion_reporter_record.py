import logging
from string import Template
from flask_restful import request, Resource, reqparse
from accessors.celery_task_accessor import CeleryTaskAccessor
from accessors.ion_reporter_accessor import IonReporterAccessor
from common.dictionary_helper import DictionaryHelper
from resource_helpers.abort_logger import AbortLogger

MESSAGE_500 = Template("Server Error contact help: $error")
MESSAGE_404 = Template("No ion reporters with id: $ion_reporter_id found")



parser = reqparse.RequestParser()
parser.add_argument('projection', type=str, required=False, action='append')


class IonReporterRecord(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get(self, ion_reporter_id):
        self.logger.info("Getting ion reporter with id: " + str(ion_reporter_id))
        args = parser.parse_args()

        try:
            results = IonReporterAccessor().scan({'ion_reporter_id': ion_reporter_id})
        except Exception as e:
            AbortLogger.log_and_abort(500, self.logger.error, MESSAGE_500.substitute(error=e.message))
        else:
            if len(results) > 0:
                if args['projection'] is not None:
                    return [{str(project): sc[str(project)] for project in args['projection'] if project in sc}
                            for sc in results]
                else:
                    return results

            AbortLogger.log_and_abort(404, self.logger.error, MESSAGE_404.substitute(ion_reporter_id=ion_reporter_id))

    def put(self, ion_reporter_id):
        self.logger.info("updating ion reporter with id: " + str(ion_reporter_id))
        args = request.json
        self.logger.debug(str(args))

        if not DictionaryHelper.has_values(args):
            AbortLogger.log_and_abort(400, self.logger.debug,
                                      "Update item failed, because data to update item with was not passed in request")

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
        except Exception as e:
            AbortLogger.log_and_abort(500, self.logger.error, MESSAGE_500.substitute(error=e.message))

        return {"message": "Ion reporter with ion reporter id: " + ion_reporter_id + " updated"}

    def delete(self, ion_reporter_id):
        self.logger.info("Deleting ion reporter with id: " + str(ion_reporter_id))
        try:
            CeleryTaskAccessor().delete_ir_item({'ion_reporter_id': ion_reporter_id})
            return {"message": "Item deleted", "ion_reporter_id": ion_reporter_id}
        except Exception as e:
            AbortLogger.log_and_abort(500, self.logger.error, MESSAGE_500.substitute(error=e.message))
