import __builtin__
import inspect
import os

from flask_restful import abort
from common.ped_match_bot import PedMatchBot

queue_name = os.environ['IR_QUEUE_NAME']
slack_channel_id = (__builtin__.environment_config[__builtin__.environment]['slack_channel_id'])

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
                PedMatchBot().send_message(channel_id=slack_channel_id,
                                           message=(
                                               "*IR ECOSYSTEM:::* Error code: *" + str(error_code) + "*" + "\n" +
                                               "Queue Name: " + "*" + queue_name + "*" + "\n" +
                                               "Error Message: *" + message + "*" + "\n" +
                                               str(PedMatchBot.generate_traceback_message(stack))
                                           )
                                           )

        abort(error_code, message=message)


