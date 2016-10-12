import os
import __builtin__

from slackclient import SlackClient


slack_client = SlackClient(os.environ.get('SLACK_TOKEN'))


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