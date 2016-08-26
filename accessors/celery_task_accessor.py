import logging
from tasks.tasks import put, write_vcf, write_message_body


# This code is pointless and can be removed later. Its only here for pedagogical purposes.

class CeleryTaskAccessor(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def put_item(self, item_dictionary):
        self.logger.debug("Celery QUEUE put_item called")
        self.logger.debug(str(item_dictionary))
        try:
            return put.delay(item_dictionary)
        except Exception, e:
            self.logger.debug("Client Error on queue put_item: " + e.message)
            raise

    def vcf_item(self, item_dictionary):
        self.logger.debug("Celery QUEUE put_item called")
        self.logger.debug(str(item_dictionary))
        try:
            # this is the only line that actually does anything interesting.
            return write_vcf.delay(item_dictionary)
        except Exception, e:
            self.logger.debug("Client Error on queue put_item: " + e.message)
            raise

    def message_body_item(self, message_body):
        self.logger.debug("Celery QUEUE, TRYING TO WRITE TO THE QUEUE")
        self.logger.debug(str(message_body))
        try:
            # this is the only line that actually does anything interesting.
            return write_message_body.delay(message_body)
        except Exception, e:
            self.logger.debug("Client Error on queue put_item: " + e.message)
            raise