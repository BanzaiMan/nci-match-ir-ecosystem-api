import inspect
from flask_restful import abort


class AbortLogger(object):

    @staticmethod
    def log_and_abort(error_code, logger_level_function, message):
        try:
            calling_function = inspect.stack()[1][3]
        except Exception as e:
            logger_level_function("Calling method not found in stack :: Log message: " + message + " :: " + e.message)
        else:
            logger_level_function("Calling Method: " + calling_function + " :: Log message: " + message)

        abort(error_code, message=message)
