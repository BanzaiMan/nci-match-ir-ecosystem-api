import __builtin__
import inspect
import datetime
import time
import json
import traceback
from slackclient import SlackClient
from celery.exceptions import MaxRetriesExceededError


class PedMatchBot(object):

    @staticmethod
    def send_message(attachments):
        SlackClient(__builtin__.slack_token).api_call(
            "chat.postMessage",
            channel=(__builtin__.environment_config[__builtin__.environment]['slack_channel_id']),

            username=__builtin__.environment_config[__builtin__.environment]['bot_name'],
            icon_emoji=__builtin__.environment_config[__builtin__.environment]['icon_emoji'],
            attachments = attachments
        )

    @staticmethod
    def upload_to_slack(message):
        SlackClient(__builtin__.slack_token).api_call(
            "files.upload",
            as_user = "true",
            filename="error_message",
            content= message,
            channels= (__builtin__.environment_config[__builtin__.environment]['slack_channel_id'])
        )

    @staticmethod
    def return_slack_message_and_retry(queue_name, message, error_message, stack, task, logger, dlx_queue):
        requeue_countdown = (__builtin__.environment_config[__builtin__.environment]['requeue_countdown'])
        details = task.request
        message_output = json.dumps(message, indent=4, sort_keys=True)
        ts = time.time()
        pattern = '%Y-%m-%d %H:%M:%S'
        time_stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        epoch = int(time.mktime(time.strptime(time_stamp, pattern)))
        upload_file = PedMatchBot.upload_to_slack(message_output)


        attachments = [
            {
                "fallback": error_message + " - : https://match.loggly.com/search#terms=",
                "color": "#ff0000",
                "pretext": error_message + "; \n Will attempt re-queue in " + str(requeue_countdown) + " seconds.",
                "title": "StackTrace and Message",
                "title_link": "https://match.loggly.com/search#terms=" + str(details.id),
                "text": "<https://match.loggly.com/search#terms=" + str(details.id) + "|ReferenceError> - Loggly",
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
                        "title": "Task ID",
                        "value": str(details.id),
                        "short": "true"
                    },
                    {
                        "title": "Retry number",
                        "value": str(details.retries),
                        "short": "true"
                    }
                ],

                "footer": "Host: " + str(details.hostname),
                "ts": epoch
            }
        ]

        retry_attachments = [
            {
                "fallback": error_message + " - : https://match.loggly.com/search#terms=",
                "color": "#ff0000",
                "pretext": error_message + "; \n Maximum retries reached, moving to to: " + queue_name + "_dlx.",
                "title": "StackTrace and Message",
                "title_link": upload_file,
                "text": "<https://match.loggly.com/search#terms=" + str(details.id) + "|ReferenceError> - Loggly",
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
                        "title": "Task ID",
                        "value": str(details.id),
                        "short": "true"
                    },
                    {
                        "title": "Estimated Time of Arrival",
                        "value": str(details.eta),
                        "short": "true"
                    }
                ],

                "footer": "Host: " + str(details.hostname),
                "ts": epoch
            }
        ]

        try:
            logger.error(str(details.task) + " has failed, details: " + str(details))
            PedMatchBot().send_message(attachments= attachments)
        except Exception as e:
            logger.error("Ped Match Bot Failure.: " + e.message)
        try:
            task.retry(args=[message], countdown=requeue_countdown)
        except MaxRetriesExceededError:
            logger.error("MAXIMUM RETRIES reached for %s moving task to %s details: %s" % (details.task, dlx_queue, details))
            PedMatchBot().send_message(attachments=retry_attachments)
            try:
                task.apply_async(args=[message], queue=dlx_queue)
            except Exception as e:
                logger.error("Unable to post to dead letter queue: %s" % e.message)

    @staticmethod
    def generate_traceback_message(stack):
        calling_function = inspect.stack()[1][3]
        error_traceback = traceback.format_exc()
        class_called = str(stack[1][0].f_locals["self"].__class__)
        ts = time.time()
        time_stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        message_details = (
            "The class, %s and method %s were called at %s \n %s" %(class_called, calling_function, time_stamp,
                                                                          error_traceback)

        )
        return message_details

