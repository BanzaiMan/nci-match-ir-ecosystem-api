import logging
import datetime
from flask_restful import request
from accessors.celery_task_accessor import CeleryTaskAccessor
from accessors.ion_reporter_accessor import IonReporterAccessor
from common.dictionary_helper import DictionaryHelper
from resource_helpers.abort_logger import AbortLogger
from table import Table

ION_REPORTER_ID_LENGTH = 5


class IonReporterTable(Table):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        Table.__init__(self, IonReporterAccessor, 'ion_reporter_id', ION_REPORTER_ID_LENGTH, 'IR_')

    def post(self):
        self.logger.info("POST Request to create a new ion reporter")
        args = request.args
        self.logger.debug(str(args))

        if 'ion_reporter_id' in args:
            AbortLogger.log_and_abort(400, self.logger.debug,
                                      "Ion reporter creation failed, because ion_reporter_id was passed in request")

        if DictionaryHelper.keys_have_value(args, ['site']):
            self.logger.debug("creating ion reporter id for site: " + str(args))

            # if user pass keys other than 'site' and 'control_type' in arguments, will ignore
            new_item_dictionary = {}
            new_item_dictionary.update({'site': args['site']})

            new_item_dictionary.update({'ion_reporter_id': self.get_unique_key(),
                                        'date_ion_reporter_id_created': str(datetime.datetime.utcnow())})

            self.logger.debug("Attempting to write: " + str(new_item_dictionary))
            try:
                # This should go directly to database do not use queue here...every other write...but not this one.
                # "Put" is correct in this case as dynamodb uses put to mean create. Even though rest uses PUT for
                # updates and POST for creation, typically. Granted in rest a put could be a creation also...but not in
                # our case.
                IonReporterAccessor().put_item(new_item_dictionary)
                return {"result": "New ion reporter created", "ion_reporter_id": new_item_dictionary['ion_reporter_id']}
            except Exception as e:
                AbortLogger.log_and_abort(500, self.logger.error, "Could not put_item because " + e.message)

        else:
            AbortLogger.log_and_abort(400, self.logger.debug,
                                      "Ion reporter creation failed, because site was not passed in.")

    def delete(self):
        self.logger.info("Ion Reporter Batch Delete called")
        args = request.args
        self.logger.debug(str(args))
        if not DictionaryHelper.has_values(args):
            AbortLogger.log_and_abort(400, self.logger.debug,
                                      "Cannot use batch delete to delete all records. "
                                      "This is just to make things a little safer.")
        try:
            self.logger.info("Deleting items based on query: " + str(args))
            CeleryTaskAccessor().delete_ir_items(args)
        except Exception as e:
            AbortLogger.log_and_abort(500, self.logger.error, "Batch delete failed because: " + e.message)

        return {"result": "Batch deletion request placed on queue to be processed"}
