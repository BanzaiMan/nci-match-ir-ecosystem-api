import inspect
from flask_restful import abort
from common.ped_match_bot import PedMatchBot


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
                PedMatchBot().send_message(
                    attachments=
                    [
                        {
                            "fallback": " HTTP Code Error",
                            "color": "#ff0000",
                            "pretext": message,
                            "title": "Loggly",
                            "title_link": "https://match.loggly.com/search#terms="+ message,
                            "fields": [
                                {
                                    "title": "Project",
                                    "value": "IR Ecosystem",
                                    "short": "true"
                                },
                                {
                                    "title": "Method Called",
                                    "value": calling_function,
                                    "short": "true"
                                }
                            ],

                            "footer": "HTTP Status Code: " + str(error_code),
                        }
                    ]
                                           )

        abort(error_code, message=message)


