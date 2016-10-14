import __builtin__
import inspect
import datetime
import time

from flask_restful import abort

from common.ped_match_bot import PedMatchBot


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
            if error_code >= 500:
                error = traceback.format_exc()
                stack = inspect.stack()
                class_called = str(stack[1][0].f_locals["self"].__class__)
                ts = time.time()
                st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                # TODO: Not quite as its not printing the correct class and the traceback needs to be the stack trace...different things.
                PedMatchBot().send_message(channel_id=slack_channel_id,
                                           message=(
                                          "*IR ECOSYSTEM:::*  The class, *" + class_called + "* and method *" +
                                          calling_function + "* were called at *" + st + "* and produced a *" +
                                          str(error_code) + "* error." + "\n" + "*Error message:* "  + message +
                                          "\n" + error )
                                           )

        abort(error_code, message=message)


