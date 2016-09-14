import logging
from flask_restful import request, Resource
from common.dictionary_helper import DictionaryHelper
from resource_helpers.abort_logger import AbortLogger
from common.string_helper import StringHelper


class Table(Resource):

    def __init__(self, accessor, key, id_len):
        self.key = key
        self.id_len = id_len
        self.accessor = accessor
        self.logger = logging.getLogger(__name__)

    def get(self):
        self.logger.info("GET called for accessor: " + self.accessor.__class__.__name__)
        args = request.args
        self.logger.debug(str(args))
        try:
            records = self.accessor().scan(args) if DictionaryHelper.has_values(args) \
                else self.accessor().scan(None)
        except Exception as e:
            AbortLogger.log_and_abort(500, self.logger.error, "Get failed because: " + e.message)
        else:
            self.logger.debug("Records: " + str(records))

            if records is None or len(records) < 1:
                AbortLogger.log_and_abort(404, self.logger.debug, "No records meet the query parameters")
            else:
                return records

    def get_unique_key(self):
        new_record_id = ""
        unique_key = False
        while not unique_key:
            new_record_id = StringHelper.generate_ion_reporter_id(self.id_len)
            results = self.accessor().get_item({self.key: new_record_id})
            self.logger.debug(results)

            if len(results) > 0:
                self.logger.info("Generated Key was not unique, so we need to try again")
            else:
                unique_key = True

        return new_record_id
