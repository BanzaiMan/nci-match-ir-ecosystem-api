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
    def send_message(message):
        SlackClient(__builtin__.slack_token).api_call(
            "chat.postMessage",
            channel=(__builtin__.environment_config[__builtin__.environment]['slack_channel_id']),
            text=message,
            username=__builtin__.environment_config[__builtin__.environment]['bot_name'],
            icon_emoji=__builtin__.environment_config[__builtin__.environment]['icon_emoji']
        )

    @staticmethod
    def return_slack_message_and_retry(queue_name, message, error_message, stack, task, logger, dlx_queue):
        requeue_countdown = (__builtin__.environment_config[__builtin__.environment]['requeue_countdown'])
        details = task.request
        message_output = json.dumps(message, indent=4, sort_keys=True)
        message_details = (
            "\n %s \n Queue Name: *%s* \n Task name: *%s* \n Task ID: *%s* \n Retry number: *%s* \n Host name: *%s* \n "
            "Estimated time of arrival: *%s* \n Error: *%s*" ) % (message_output, queue_name, details.task,
                                                                     details.id, details.retries, details.hostname,
                                                                     details.eta, error_message)
        try:
            logger.error(str(details.task) + " has failed, details: " + str(details))
            PedMatchBot().send_message(
                                       message=("*IR ECOSYSTEM:::* Error processing: \n %s \n %s Re-queueing to attempt after: *%s seconds.*"
                                                % (message_details, PedMatchBot.generate_traceback_message(stack), requeue_countdown)
                                                ))
        except Exception as e:
            logger.error("Ped Match Bot Failure.: " + e.message)
        try:
            task.retry(args=[message], countdown=requeue_countdown)
        except MaxRetriesExceededError:
            logger.error("MAXIMUM RETRIES reached for %s moving task to %s details: %s" % (details.task, dlx_queue, details))
            PedMatchBot().send_message(
                                       message=(
                                           "*IR ECOSYSTEM:::* Maximum retries reached for: %s \n %s Moving to queue: *%s_dlx.*"
                                           % (message_details, PedMatchBot.generate_traceback_message(stack), queue_name)
                                       )
            )
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
            "The class, *%s* and method *%s* were called at *%s* \n %s" %(class_called, calling_function, time_stamp,
                                                                          error_traceback)

        )
        return message_details

