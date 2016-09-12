import logging
import datetime
from string import Template
from flask_restful import request, reqparse, Resource
from accessors.celery_task_accessor import CeleryTaskAccessor
from accessors.ion_reporter_accessor import IonReporterAccessor
from common.dictionary_helper import DictionaryHelper
from common.string_helper import StringHelper
from resource_helpers.abort_logger import AbortLogger

MESSAGE_500 = Template("Server Error contact help: $error")
MESSAGE_404 = Template("No ion reporters with id: $ion_reporter_id found")

parser = reqparse.RequestParser()
parser.add_argument('ion_reporter_id', type=str, required=False, location='json', help="'ion_reporter_id' is required")

ION_REPORTER_ID_LENGTH = 5


class IonReporterTable(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get(self):
        self.logger.info("Ion reporter GET called")
        args = request.args
        self.logger.debug(str(args))
        try:
            ion_reporter = IonReporterAccessor().scan(args) if DictionaryHelper.has_values(args) \
                else IonReporterAccessor().scan(None)
        except Exception as e:
            AbortLogger.log_and_abort(500, self.logger.error, "Get failed because: " + e.message)
        else:
            self.logger.debug("Ion Reporter: " + str(ion_reporter))

            if ion_reporter is None:
                AbortLogger.log_and_abort(404, self.logger.debug, "No ion reporters meet the query parameters")
            else:
                return ion_reporter

    def post(self):
        self.logger.info("POST Request to create a new ion reporter")
        args = request.args
        self.logger.debug(str(args))

        if 'ion_reporter_id' in args:
            AbortLogger.log_and_abort(400, self.logger.debug,
                                      "Ion reporter creation failed, because ion_reporter_id was passed in request")

        if DictionaryHelper.keys_have_value(args, ['site']):
            self.logger.debug("creating ion reporter id for site: " + str(args))

            new_item_dictionary = args.copy()
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
                AbortLogger.log_and_abort(500, self.logger.error, MESSAGE_500.substitute(error=e.message))

        else:
            AbortLogger.log_and_abort(400, self.logger.debug,
                                      "Must send in a site in order to create an ion reporter record")

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
            AbortLogger.log_and_abort(500, self.logger.error, MESSAGE_500.substitute(error=e.message))

        return {"result": "Batch deletion request placed on queue to be processed"}

    def get_unique_key(self):
        new_ion_reporter_id = ""
        unique_key = False
        while not unique_key:
            new_ion_reporter_id = StringHelper.generate_ion_reporter_id(ION_REPORTER_ID_LENGTH)
            results = IonReporterAccessor().get_item({'ion_reporter_id': new_ion_reporter_id})
            self.logger.debug(results)

            if len(results) > 0:
                self.logger.info("Generated Key was not unique, so we need to try again")
            else:
                unique_key = True

        return new_ion_reporter_id