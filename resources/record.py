import logging
from string import Template
from flask_restful import request, Resource
from common.dictionary_helper import DictionaryHelper
from resource_helpers.abort_logger import AbortLogger
import json
import re

MESSAGE_500 = Template("Server Error contact help: $error")
MESSAGE_404 = Template("No $class_name with id: $key_value found")


class Record(Resource):
    def __init__(self, celery_accessor, database_accessor, key_name, task_suffix):
        self.task_suffix = task_suffix
        self.celery_accessor = celery_accessor
        self.database_accessor = database_accessor
        self.key_name = key_name
        self.logger = logging.getLogger(__name__)

    def get(self, identifier):
        self.logger.info("Getting " + self.database_accessor.__class__.__name__ + " with id: " + str(identifier))

        args = request.args
        projection_list, args = DictionaryHelper.get_projection(args)
        try:
            results = self.database_accessor().get_item({self.key_name: identifier}, ','.join(projection_list))
        except Exception as e:
            AbortLogger.log_and_abort(500, self.logger.error, MESSAGE_500.substitute(error=e.message))
        else:
            if len(results) > 0:
                self.logger.debug("Found: " + str(results))
                #return results
                # this is a temporary solution to convert json string to real json format
                # variants are stored in Dynamodb as string. Should store them as list of dictionary
                convert_results = {}
                for key, value in results.iteritems():
                    value = value.replace("None", "null")
                    value = value.replace("True", "true")
                    value = value.replace("False", "false")
                    value = value.replace("'", '"')
                    if re.search("\":", value):
                        value = json.loads(value)
                    convert_results.update({key: value})
                return convert_results

            AbortLogger.log_and_abort(404, self.logger.debug,
                                      MESSAGE_404.substitute(class_name=self.database_accessor.__class__.__name__,
                                                             key_value=identifier))

    def put(self, identifier):
        self.logger.info("updating " + self.database_accessor.__class__.__name__ +
                         " with id: " + str(identifier))
        args = request.json
        self.logger.debug(str(args))

        if not DictionaryHelper.has_values(args):
            AbortLogger.log_and_abort(400, self.logger.debug,
                                      "Update item failed, because data to update item with was not passed in request")

        item_dictionary = args.copy()
        item_dictionary.update({self.key_name: identifier})

        # Very important line of code this takes all of the 'None' values out of the dictionary.
        # Without this, the record would update all attributes in the params above with 'None' unless they
        # were explicitly passed in. In reality, we only want to update the attributes that have been explicitly
        # passed in from the params. If they haven't been passed in then they shouldn't be updated.
        item_dictionary = dict((k, v) for k, v in item_dictionary.iteritems() if v)

        if self.record_exist(identifier):
            try:
                update = getattr(self.celery_accessor(), 'update' + self.task_suffix)
                update(item_dictionary)
                # self.celery_accessor().update_ion_reporter_record(item_dictionary)
            except Exception as e:
                #AbortLogger.log_and_abort(500, self.logger.error, MESSAGE_500.substitute(error=e.message))
                AbortLogger.log_and_abort(500, self.logger.error, "Failed to update " + identifier + ", because : " + e.message)
            else:
                return {"message": self.database_accessor.__class__.__name__ + " with id: " + identifier + " updated"}
        else:
            AbortLogger.log_and_abort(404, self.logger.error,
                                      MESSAGE_404.substitute(class_name=self.database_accessor.__class__.__name__,
                                                             key_value=identifier))

    def delete(self, identifier):
        self.logger.info("Deleting " + self.database_accessor.__class__.__name__ +
                         " with id: " + str(identifier))

        if self.record_exist(identifier):
            try:
                delete = getattr(self.celery_accessor(), 'delete' + self.task_suffix)
                delete({self.key_name: identifier})
                # self.celery_accessor().delete_ir_item()
            except Exception as e:
                #AbortLogger.log_and_abort(500, self.logger.error, MESSAGE_500.substitute(error=e.message))
                AbortLogger.log_and_abort(500, self.logger.error, "Failed to delete " + identifier + ", because : " + e.message)
            else:
                return {"message": "Item deleted", self.key_name: identifier}
        else:
            AbortLogger.log_and_abort(404, self.logger.error,
                                      MESSAGE_404.substitute(class_name=self.database_accessor.__class__.__name__,
                                                             key_value=identifier))

    def record_exist(self, identifier):
        try:
            results = self.get(identifier)
        except Exception as e:
            #AbortLogger.log_and_abort(500, self.logger.error, MESSAGE_500.substitute(error=e.message))
            AbortLogger.log_and_abort(404, self.logger.error, identifier + " does not exist. " + e.message)
        else:
            return len(results) > 0
