from aws_sqs_accessor import AwsSqsAccessor

class SequencerFileQueue(AwsSqsAccessor):
        def __init__(self):
            super(SequencerFileQueue, self).__init__('after_s3_upload')

        def write(self, message):
            self.queue.send_message(MessageBody=message)
