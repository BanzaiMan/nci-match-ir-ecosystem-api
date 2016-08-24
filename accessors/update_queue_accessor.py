from sqs_accessor import SqsAccessor

class UpdateQueueAccessor(SqsAccessor):
        def __init__(self):
            SqsAccessor.__init__(self, 'update_queue','us-east-1')

<<<<<<< HEAD
        # # TODO: Add logging
        # # TODO: What if it fails to write, like the queue is down? Should catch errors and return errors.
=======
>>>>>>> origin/master
        def write(self, message):
            self.logger.info('Attempting to POST new message to queue')
            try:
                self.queue.send_message(MessageBody=message)
                self.logger.info('New message has been POSTED to SQS queue successfully')
            except Exception, e:
                self.logger.error("Write function failed, problem passing queue properties: " + e.message)
                raise
