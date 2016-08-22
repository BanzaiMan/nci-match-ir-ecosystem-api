from sqs_accessor import SqsAccessor


# TODO: Lets talk about these queues...perhaps we just need a single queue with a flag?
class UpdateQueueAccessor(SqsAccessor):
        def __init__(self):
            super(UpdateQueueAccessor, self).__init__('update_queue')

        # TODO: Add logging
        # TODO: What if it fails to write, like the queue is down? Should catch errors and return errors.
        def write(self, message):
                self.queue.send_message(MessageBody=message)
