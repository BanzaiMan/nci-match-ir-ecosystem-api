import logging
import datetime
from flask_restful import request

from accessors.celery_task_accessor import CeleryTaskAccessor
from accessors.sample_control_accessor import SampleControlAccessor
from common.dictionary_helper import DictionaryHelper
from resource_helpers.abort_logger import AbortLogger
from table import Table

MOLECULAR_ID_LENGTH = 5


class SampleControlTable(Table):

    """This class is a tiny bit inconsistent by design. The argument types are all optional for the 'GET' but only the
    control_type and site are needed and required for the 'POST.' Passing in any other query parameters to the POST
    will result in an error message being returned. Technically, it would be better to put the post in yet another
    class but  then we end up with 3 classes to handle sample controls (1. One for general queries 'get', 2. One
    for updates 'put, delete' 3. and yet another one for the POST.) That situation, while perfectly consistent with
    REST standards, creates a lot of redundant code. As it is, we have 2 sample control classes."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        Table.__init__(self, SampleControlAccessor, 'molecular_id', MOLECULAR_ID_LENGTH, 'SC_')

    def delete(self):
        self.logger.info("Sample control Batch Delete called")
        args = request.args
        self.logger.debug(str(args))
        if not DictionaryHelper.has_values(args):
            AbortLogger.log_and_abort(400, self.logger.debug,
                                      "Cannot use batch delete to delete all records. "
                                      "This is just to make things a little safer.")
        self.logger.info("Deleting items based on query: " + str(args))
        try:
            CeleryTaskAccessor().delete_items(args)
        except Exception as e:
            AbortLogger.log_and_abort(500, self.logger.error, "Batch delete failed because: " + e.message)

        return {"result": "Batch deletion request placed on queue to be processed"}

    # This is the method is not being perfectly consistent with standards.
    # all things considered this seems best for now unless a non verbose way can be thought up.
    # Go directly to database...do not change to use queue because we need the molecular_id back and written
    # Also note that while the rest call is "POST" the database call is "put_item" Dynamodb just uses the word "put"
    # to indicate creation whereas REST uses "put" more often for "update" and POST for creation.

    # control_type and site are essential for POST, all other parameters are ignored on post except molecular_id
    # which, if passed in will cause a failure. The proper order is to first POST to get a molecular_id then to PUT
    # the files using the molecular_id in the URI. From there other fields can be updated if needed.
    def post(self):
        self.logger.info("POST Request to create a new sample control")
        args = request.args
        self.logger.debug(str(args))

        if 'molecular_id' in args:
            AbortLogger.log_and_abort(400, self.logger.debug,
                                      "Sample Control creation failed, because molecular_id was passed in request")

        if DictionaryHelper.keys_have_value(args, ['control_type', 'site']):
            self.logger.debug("Sample Control creation failed, because request molecular_id was passed in")

            # Yes this will store whatever is passed in with args when created..that is what we want.
            new_item_dictionary = args.copy()
            new_item_dictionary.update({'molecular_id': self.get_unique_key(),
                                        'date_molecular_id_created': str(datetime.datetime.utcnow())})

            self.logger.debug("Attempting to write: " + str(new_item_dictionary))
            try:
                # This should go directly to database do not use queue here...every other write...but not this one.
                # "Put" is correct in this case as dynamodb uses put to mean create. Even though rest uses PUT for
                # updates and POST for creation, typically. Granted in rest a put could be a creation also...but not in
                # our case.
                SampleControlAccessor().put_item(new_item_dictionary)
                return {"result": "New sample control created", "molecular_id": new_item_dictionary['molecular_id']}
            except Exception as e:
                AbortLogger.log_and_abort(500, self.logger.error, "Could not put_item because " + e.message)

        else:
            AbortLogger.log_and_abort(400, self.logger.debug,
                                      "Sample Control creation failed, "
                                      "because both site and control_type were not passed in")
