import inspect
from flask_restful import abort
from resource_helpers.ped_match_bot import PedBot

class AbortLogger(object):

    @staticmethod
    def log_and_abort(error_code, logger_level_function, message):
        try:
            calling_function = inspect.stack()[1][3]
        except Exception as e:
            logger_level_function("Calling method not found in stack :: Log message: " + message + " :: " + e.message)
        else:
            logger_level_function("Calling Method: " + calling_function + " :: Log message: " + message)
        # TODO: Waleed should be inside else and also want to log the calling_function just like the line above so that someone reading the message will understand the context.
        if error_code == 500:
            PedBot().send_message(channel_id='C2N1BJX0U', message='This is a a 500 error: ' + message)

        abort(error_code, message=message)


