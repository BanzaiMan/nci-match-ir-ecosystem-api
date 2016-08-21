from aws_sqs_accessor import AwsSqsAccessor


class SequencerFileQueue(AwsSqsAccessor):
        # TODO: Rename queue to 'WHAT it contains' instead of naming it to'WHEN it is used' as we may change the WHEN
        def __init__(self):
            super(SequencerFileQueue, self).__init__('after_s3_upload')

        # TODO: What if it fails to write, like the queue is down? Should catch errors and return errors.
        def write(self, message):
            self.queue.send_message(MessageBody=message)
