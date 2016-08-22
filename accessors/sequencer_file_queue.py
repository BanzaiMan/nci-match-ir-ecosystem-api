from aws_sqs_accessor import AwsSqsAccessor


# TODO: Lets talk about these queues...perhaps we just need a single queue with a flag?
class SequencerFileQueue(AwsSqsAccessor):
        def __init__(self):
            super(SequencerFileQueue, self).__init__('files_from_ir_sequencer')

        # TODO: Add logging
        # TODO: What if it fails to write, like the queue is down? Should catch errors and return errors.
        def write(self, message):
                self.queue.send_message(MessageBody=message)
