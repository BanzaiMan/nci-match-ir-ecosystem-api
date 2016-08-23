from sqs_accessor import SqsAccessor
import __builtin__


class UpdateQueueAccessor(SqsAccessor):
        def __init__(self):
            SqsAccessor.__init__(self, 'update_queue',
                                 __builtin__.environment_config[__builtin__.environment]['region'])

        # TODO: Add logging
        # TODO: What if it fails to write, like the queue is down? Should catch errors and return errors.
        def write(self, message):
                self.queue.send_message(MessageBody=message)
