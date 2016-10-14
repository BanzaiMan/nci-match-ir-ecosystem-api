import logging
import os
import __builtin__

from logging.config import fileConfig
from slackclient import SlackClient
from common.environment_helper import EnvironmentHelper

# Logging functionality
fileConfig(os.path.abspath("config/logging_config.ini"))
logger = logging.getLogger(__name__)

EnvironmentHelper.set_environment(logger.info)
slack_client = SlackClient(os.environ.get('SLACK_TOKEN'))

# TODO: Waleed our standards are that class name should match file name except file name is snake case and class name is camel case.
class PedBot(object):
    @staticmethod
    def send_message(channel_id, message):

        bot_name = (__builtin__.environment_config[__builtin__.environment]['bot_name'])
        slack_client.api_call(
            "chat.postMessage",
            channel=channel_id,
            text=message,
            username=bot_name,
            icon_emoji=':face_with_head_bandage:'
        )