import boto3

# Created a class for accessing the AWS SQS, with us-west as default

class AwsSqsAccessor(object):
    def __init__(self, queue_name, region_name='us-west-2'):
        self.queue_name = queue_name
        self.region_name = region_name
        self.sqs = boto3.resource('sqs', region_name=self.region_name)
        self.queue = self.sqs.get_queue_by_name(QueueName=self.queue_name)
