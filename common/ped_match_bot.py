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
    def send_message(channel_id, message):
        SlackClient(__builtin__.slack_token).api_call(
            "chat.postMessage",
            channel=channel_id,
            text=message,
            username=__builtin__.environment_config[__builtin__.environment]['bot_name'],
            icon_emoji=__builtin__.environment_config[__builtin__.environment]['icon_emoji']
        )

    @staticmethod
    def return_slack_message_and_retry(queue_name, message, error_message, stack, task, logger, dlx_queue):
        slack_channel_id = (__builtin__.environment_config[__builtin__.environment]['slack_channel_id'])
        requeue_countdown = (__builtin__.environment_config[__builtin__.environment]['requeue_countdown'])
        details = task.request
        message_output = json.dumps(message, indent=4, sort_keys=True)
        message_details = (
            "\n" + str(message_output)
            + "\n" + "Queue Name: " + "*" + queue_name + "*" + "\n" +
            "Task name: " + "*" + str(details.task) + "*" + "\n" +
            "Task ID: " + "*" + str(details.id) + "*" + "\n" +
            "Message headers: " + "*" + str(details.headers) + "*" + "\n" +
            "Retry number: " + "*" + str(details.retries) + "*" + "\n" +
            "Host name: " + "*" + str(details.hostname) + "*" + "\n" +
            "Estimated time of arrival: " + "*" + str(details.eta) + "*" + "\n" +
            "Error: *" + error_message + "*" + "\n" )
        try:
            logger.error(str(details.task) + " has failed, details: " + str(details))
            PedMatchBot().send_message(channel_id=slack_channel_id,
                                       message=("*IR ECOSYSTEM:::* Error processing: " + "\n" +
                                                message_details +
                                                str(PedMatchBot.generate_traceback_message(stack))
                                                + "Re-queueing to attempt after: " + "*" + str(requeue_countdown) +
                                                " seconds." + "*"
                                                ))
        except Exception as e:
            logger.error("Ped Match Bot Failure.: " + e.message)
        try:
            task.retry(args=[message], countdown=requeue_countdown)
        except MaxRetriesExceededError:
            logger.error("Maximum retries reached for " + str(details.task) + " moving task to " + dlx_queue +
                         " details: " + str(details))
            PedMatchBot().send_message(channel_id=slack_channel_id,
                                       message=("*IR ECOSYSTEM:::* Maximum retries reached for: " + "\n" +
                                                message_details +
                                                PedMatchBot.generate_traceback_message(stack)))
            try:
                task.apply_async(args=[message], queue=dlx_queue)
            except Exception as e:
                logger.error("Unable to post to dead letter queue: " + e.message)

    @staticmethod
    def generate_traceback_message(stack):
        calling_function = inspect.stack()[1][3]
        error_traceback = traceback.format_exc()
        class_called = str(stack[1][0].f_locals["self"].__class__)
        ts = time.time()
        time_stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        message_details = (
            "  The class, *" + str(class_called) + "* and method *" + calling_function
               + "* were called at *" + time_stamp + "*" + "\n" + error_traceback

        )
        return message_details

