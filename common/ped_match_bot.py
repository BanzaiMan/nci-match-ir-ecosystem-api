import __builtin__
import inspect
import datetime
import time
import ast
import json
import traceback
import logging
from slackclient import SlackClient


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
    def return_stack(queue_name, message, error_message, stack):
        slack_channel_id = (__builtin__.environment_config[__builtin__.environment]['slack_channel_id'])
        try:
            uni_free_message = ast.literal_eval(json.dumps(message))
            PedMatchBot().send_message(channel_id=slack_channel_id,
                                       message=("*IR ECOSYSTEM:::* Error processing: " + "*" + str(uni_free_message)
                                                + "\n" + "Queue Name: " + "*" + queue_name + "*" + "\n" +
                                                "Re-queueing to attempt again in *3 hours.*" + "\n" +
                                                "Error: " + error_message + "\n" +
                                                str(PedMatchBot.generate_traceback_message(stack))))
        except Exception as e:
            logging.getLogger(__name__).error("Ped Match Bot Failure.: " + e.message)

    @staticmethod
    def generate_traceback_message(stack):
        calling_function = inspect.stack()[1][3]
        error_traceback = traceback.format_exc()
        class_called = str(stack[1][0].f_locals["self"].__class__)
        ts = time.time()
        time_stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        return "  The class, *" + str(class_called) + "* and method *" + calling_function \
               + "* were called at *" + time_stamp + "*" + "\n" + error_traceback

