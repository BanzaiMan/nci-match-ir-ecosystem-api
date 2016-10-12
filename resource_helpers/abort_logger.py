import inspect
from flask_restful import abort
import __builtin__
from resource_helpers.ped_match_bot import PedBot


class AbortLogger(object):

    @staticmethod
    def log_and_abort(error_code, logger_level_function, message):
        slack_channel_id = (__builtin__.environment_config[__builtin__.environment]['slack_channel_id'])
        try:
            calling_function = inspect.stack()[1][3]
        except Exception as e:
            logger_level_function("Calling method not found in stack :: Log message: " + message + " :: " + e.message)
        else:
            logger_level_function("Calling Method: " + calling_function + " :: Log message: " + message)
            if error_code == 500:
                PedBot().send_message(channel_id=slack_channel_id, message="Calling Method: " + calling_function +
                                                                           " :: Log message: " + message)

        abort(error_code, message=message)


