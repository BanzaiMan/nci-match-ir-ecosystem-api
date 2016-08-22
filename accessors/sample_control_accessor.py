import logging
from dynamodb_accessor import DynamoDBAccessor


class SampleControlAccessor(DynamoDBAccessor):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("SampleControlAccessor instantiated")
        DynamoDBAccessor.__init__(self, 'sample_controls')
