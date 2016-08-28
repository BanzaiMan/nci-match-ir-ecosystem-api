import logging
from tasks.tasks import put, process_ir_file, update, delete


class CeleryTaskAccessor(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_file(self, item_dictionary):
        return self.__process_item(item_dictionary, process_ir_file, "process_ir_file")

    def put_item(self, item_dictionary):
        return self.__process_item(item_dictionary, put, "put")

    def update_item(self, item_dictionary):
        return self.__process_item(item_dictionary, update, "update")

    def delete_item(self, item_dictionary):
        return self.__process_item(item_dictionary, delete, "delete")

    def __process_item(self, item_dictionary, task, task_description):
        self.logger.debug("Celery " + task_description + " called")
        self.logger.debug(str(item_dictionary))
        try:
            return task.delay(item_dictionary)
        except Exception, e:
            self.logger.debug("Client Error on celery " + task_description + ": " + e.message)
            raise
