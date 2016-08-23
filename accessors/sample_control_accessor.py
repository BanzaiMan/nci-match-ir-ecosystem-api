import logging
import __builtin__
from dynamodb_accessor import DynamoDBAccessor


class SampleControlAccessor(DynamoDBAccessor):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("SampleControlAccessor instantiated")
        self.logger.debug("__builtin__.environment: " + str(__builtin__.environment))
        self.logger.debug("__builtin__.environment_config: " + str(__builtin__.environment_config))
        DynamoDBAccessor.__init__(self, 'sample_controls',
                                  __builtin__.environment_config[__builtin__.environment]['dynamo_endpoint'],
                                  __builtin__.environment_config[__builtin__.environment]['region'])
