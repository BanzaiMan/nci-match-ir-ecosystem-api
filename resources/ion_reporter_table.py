import logging
import datetime
from flask_restful import abort, request, reqparse, Resource

from accessors.celery_task_accessor import CeleryTaskAccessor
from accessors.ion_reporter_accessor import IonReporterAccessor
from common.dictionary_helper import DictionaryHelper
from common.string_helper import StringHelper

parser = reqparse.RequestParser()
# TODO: Create a means to store, retrieve, delete, and update information about the ion reporters themselves


ION_REPORTER_ID_LENGTH = 5

class IonReporterTable(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

# TODO begin here WAiO

    def get(self):
        self.logger.info("Ion reporter GET called")
        args = request.args
        self.logger.debug(str(args))
        try:
            ion_reporter = IonReporterAccessor().scan(args)
            self.logger.debug(str(ion_reporter))
            return ion_reporter if ion_reporter is not None else \
                abort(404, message="No ion reporters meet the query parameters")
        except Exception, e:
            self.logger.error("Get failed because: " + e.message)
            abort(500, message="Get failed because: " + e.message)

    def post(self):
        self.logger.info("POST Request to create a new ion reporter record")
        args = request.args
        self.logger.debug(str(args))

        if 'ion_reporter_id' in args:
            self.logger.debug("Ion reporter creation failed, because ion_reporter_id was passed in request")
            abort(400, message="ion_reporter_id is not a valid input when attempting to create a new ion reporter record."
                               "The post will create the id for you. Simply pass in site'")

        if DictionaryHelper.keys_have_value(args, ['site']):
            self.logger.debug("Ion reporter record creation failed, because request ion_reporter_id was passed in")

            new_item_dictionary = args.copy()
            new_item_dictionary.update({'ion_reporter_id': self.__get_unique_key(),
                                        'date_ion_reporter_id_created': str(datetime.datetime.utcnow())})

            self.logger.debug("Attempting to write: " + str(new_item_dictionary))
            try:
                # This should go directly to database do not use queue here...every other write...but not this one.
                # "Put" is correct in this case as dynamodb uses put to mean create. Even though rest uses PUT for
                # updates and POST for creation, typically. Granted in rest a put could be a creation also...but not in
                # our case.
                IonReporterAccessor().put_item(new_item_dictionary)
                return {"result": "New ion reporter record created", "ion_reporter_id": new_item_dictionary['ion_reporter_id']}
            except Exception, e:
                self.logger.error("Could not put_item because " + e.message)
                abort(500, message="put_item failed because " + e.message)

        else:
            self.logger.debug("Ion reporter record creation failed, because site was not passed in")
            abort(400, message="Must send in a site in order to create an ion reporter record")

    def put(self):
        abort(500, message="Not yet implemented")

    def delete(self):
        self.logger.info("Ion Reporter Batch Delete called")
        args = request.args
        self.logger.debug(str(args))
        if not DictionaryHelper.has_values(args):
            abort(400, message="Cannot use batch delete to delete all records. "
                               "This is just to make things a little safer.")
        try:
            self.logger.info("Deleting items based on query: " + str(args))
            CeleryTaskAccessor().delete_items(args)
        except Exception, e:
            self.logger.error("Batch delete failed because: " + e.message)
            abort(500, message="Batch delete failed because: " + e.message)

        return {"result": "Batch deletion request placed on queue to be processed"}
    def __get_unique_key(self):
        new_ion_reporter_id = ""
        unique_key = False
        while not unique_key:
            new_ion_reporter_id = StringHelper.generate_ion_reporter_id(ION_REPORTER_ID_LENGTH)
            results = IonReporterAccessor().get_item({'ion_reporter_id': new_ion_reporter_id})
            self.logger.debug(results)

            if 'Items' in results:
                self.logger.info("Generated Key was not unique, so we need to try again")
            else:
                unique_key = True

        return new_ion_reporter_id