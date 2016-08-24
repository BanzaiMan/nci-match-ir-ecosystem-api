from sqs_accessor import SqsAccessor
import __builtin__


class UpdateQueueAccessor(SqsAccessor):
        def __init__(self):
            SqsAccessor.__init__(self, 'update_queue','us-east-1')

        def write(self, message):
            self.logger.info('Attempting to POST new message to queue')
            try:
                self.queue.send_message(MessageBody=message)
                self.logger.info('New message has been POSTED to SQS queue successfully')
            except Exception, e:
                self.logger.error("Write function failed, problem passing queue properties: " + e.message)
                raise