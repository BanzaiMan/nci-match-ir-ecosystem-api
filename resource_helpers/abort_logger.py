import inspect
import os
import json
from string import Template
from tasks.tasks import app
from flask_restful import abort
from common.ped_match_bot import PedMatchBot

queue_name = app.conf.CELERY_DEFAULT_QUEUE

class AbortLogger(object):

    @staticmethod
    def log_and_abort(error_code, logger_level_function, message):
        try:
            calling_function = inspect.stack()[1][3]
        except Exception as e:
            logger_level_function("Calling method not found in stack :: Log message: " + message + " :: " + e.message)

        else:
            logger_level_function("Calling Method: " + calling_function + " :: Log message: " + message)
            if error_code >= 500:
                stack = inspect.stack()
                class_called = str(stack[1][0].f_locals["self"].__class__)

                filein = open(os.path.abspath("config/ped_match_bot_message.txt"))
                src = Template(filein.read())
                d = {'error_message': message, 'requeue_countdown': 'None', 'task_id': 'None',
                     'stack_url': 'None', 'json_url': 'None', 'queue_name': 'None',
                     'task_retries': 'None',
                     'task_hostname': 'HTTP Status Code ' + str(error_code), 'time_stamp': 'None'
                     }

                attachments = src.substitute(d)
                attachments = json.loads(attachments, strict=False)

                PedMatchBot().send_message(
                    attachments=attachments
                                           )

        abort(error_code, message=message)


