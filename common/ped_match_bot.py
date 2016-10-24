import __builtin__
import os
import inspect
import ast
import json
import logging
from slackclient import SlackClient
from logging.config import fileConfig
from common.traceback_message import TracebackError
from common.environment_helper import EnvironmentHelper

slack_client = SlackClient(os.environ.get('SLACK_TOKEN'))

fileConfig(os.path.abspath("config/logging_config.ini"))
logger = logging.getLogger(__name__)
EnvironmentHelper.set_environment(logger)

class PedMatchBot(object):

    @staticmethod
    def send_message(channel_id, message):

        bot_name = (__builtin__.environment_config[__builtin__.environment]['bot_name'])
        icon_emoji = (__builtin__.environment_config[__builtin__.environment]['icon_emoji'])
        slack_client.api_call(
            "chat.postMessage",
            channel=channel_id,
            text=message,
            username=bot_name,
            icon_emoji=icon_emoji
        )


    @staticmethod
    def return_stack(message, ex):
        slack_channel_id = (__builtin__.environment_config[__builtin__.environment]['slack_channel_id'])
        try:
            stack = inspect.stack()
            uni_free_message = ast.literal_eval(json.dumps(message))
            PedMatchBot().send_message(channel_id=slack_channel_id,
                                       message=("*IR ECOSYSTEM:::* Error processing: " + "*" + str(uni_free_message) +
                                                "*, will attempt again in *3 hours.*" + "\n" +
                                                TracebackError().generate_traceback_message(stack)))
            logger.error("Cannot process file because: " + ex.message + ", will attempt again in 3 hours.")
        except Exception as e:
            logger.error("Ped Match Bot Failure.: " + e.message)
