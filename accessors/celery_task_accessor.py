import logging
from tasks.tasks import put, ir_file


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

    def process_file(self, item_dictionary):
        self.logger.debug("Celery QUEUE put_item called")
        self.logger.debug(str(item_dictionary))
        try:
            # this is the only line that actually does anything interesting.
            return ir_file.delay(item_dictionary)
        except Exception, e:
            self.logger.debug("Client Error on queue put_item: " + e.message)
            raise
