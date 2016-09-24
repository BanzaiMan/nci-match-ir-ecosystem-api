import logging
from tasks.tasks import put, process_ir_file, update, delete, batch_delete, update_ir, batch_delete_ir, delete_ir


class CeleryTaskAccessor(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_file(self, item_dictionary):
        return self.__process_item(item_dictionary, process_ir_file, "process_ir_file")

    def put_item(self, item_dictionary):
        return self.__process_item(item_dictionary, put, "put")

    def update_sample_control_record(self, item_dictionary):
        return self.__process_item(item_dictionary, update, "update")

    def update_ion_reporter_record(self, item_dictionary):
        return self.__process_item(item_dictionary, update_ir, "update ir")

    def delete_sample_control_record(self, item_dictionary):
        return self.__process_item(item_dictionary, delete, "delete")

    def delete_ion_reporter_record(self, item_dictionary):
        return self.__process_item(item_dictionary, delete_ir, "delete ir")

    def delete_items(self, query_parameters):
        return self.__process_item(query_parameters, batch_delete, " batch delete")

    def delete_ir_items(self, query_parameters):
        return self.__process_item(query_parameters, batch_delete_ir, " batch ir delete")

    def __process_item(self, item_dictionary, task, task_description):
        self.logger.debug("Celery " + task_description + " called")
        self.logger.debug(str(item_dictionary))
        try:
            return task.delay(item_dictionary)
        except Exception as e:
            self.logger.debug("Client Error on celery " + task_description + ": " + e.message)
            raise
