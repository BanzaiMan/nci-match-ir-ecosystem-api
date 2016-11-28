import inspect
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
                PedMatchBot().send_message(
                    attachments=
                    [
                        {
                            "fallback": " HTTP Code Error",
                            "color": "#ff0000",
                            "pretext": 'Abortlogger error: ' + message,
                            "title": "Loggly Reference",
                            "title_link": "https://match.loggly.com/search#terms="+ message,
                            "fields": [
                                {
                                    "title": "Project",
                                    "value": "IR Ecosystem",
                                    "short": "true"
                                },
                                {
                                    "title": "Queue Name",
                                    "value": queue_name,
                                    "short": "true"
                                },
                                {
                                    "title": "Function",
                                    "value": calling_function,
                                    "short": "true"
                                },
                                {
                                    "title": "Class",
                                    "value": class_called,
                                    "short": "true"
                                }
                            ],

                            "footer": "HTTP Status Code: " + str(error_code),
                        }
                    ]
                                           )

        abort(error_code, message=message)


