import boto3
import logging


# TODO: I believe us-east-1 should be the default
# Created a class for accessing the AWS SQS, with us-west as default
class SqsAccessor(object):
    def __init__(self, queue_name, region_name='us-west-2'):
        self.logger = logging.getLogger(__name__)
        self.logger.info("SqsAccessor instantiated queue:" + queue_name + "::region: " + region_name)
        self.queue_name = queue_name
        self.region_name = region_name
        self.sqs = boto3.resource('sqs', region_name=self.region_name)
        self.queue = self.sqs.get_queue_by_name(QueueName=self.queue_name)
