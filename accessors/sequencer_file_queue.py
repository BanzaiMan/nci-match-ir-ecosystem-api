from aws_sqs_accessor import AwsSqsAccessor


class SequencerFileQueue(AwsSqsAccessor):
        def __init__(self):
            super(SequencerFileQueue, self).__init__('files_from_ir_sequencer')

        # TODO: What if it fails to write, like the queue is down? Should catch errors and return errors.
        def write(self, message):
            print 'Hello'
            self.queue.send_message(MessageBody=message)