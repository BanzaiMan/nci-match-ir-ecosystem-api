import logging
from tasks.tasks import put


class CeleryTaskAccessor(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def put_item(self, item_dictionary):
        self.logger.debug("Celery QUEUE put_item called")
        self.logger.debug(str(item_dictionary))
        try:
            return put.delay(item_dictionary)
        except Exception, e:
            self.logger.debug("Client Error on queuue put_item: " + e.message)
            raise
