import logging
import __builtin__
from dynamodb_accessor import DynamoDBAccessor

KEY = 'molecular_id'


class SampleControlAccessor(DynamoDBAccessor):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("SampleControlAccessor instantiated")
        self.logger.debug("__builtin__.environment: " + str(__builtin__.environment))
        self.logger.debug("__builtin__.environment_config: " + str(__builtin__.environment_config))
        DynamoDBAccessor.__init__(self, 'sample_controls',
                                  __builtin__.environment_config[__builtin__.environment]['dynamo_endpoint'],
                                  __builtin__.environment_config[__builtin__.environment]['region'])

    def create_table(self):
        pass

    def update(self, item_dictionary):
        sample_control_table_key = str(item_dictionary.pop(KEY))
        self.logger.debug(sample_control_table_key)
        try:
            return self.update_item(item_dictionary, dict(molecular_id=sample_control_table_key))
        except Exception, e:
            self.logger.debug("update_item exception in dynamodb: " + e.message)
            raise

