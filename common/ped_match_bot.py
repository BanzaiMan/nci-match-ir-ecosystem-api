import __builtin__


class PedMatchBot(object):

    @staticmethod
    def send_message(channel_id, message):
        # TODO: Don't hardcode
        bot_name = (__builtin__.environment_config[__builtin__.environment]['bot_name'])
        __builtin__.slack_token.api_call(
            "chat.postMessage",
            channel=channel_id,
            text=message,
            username=bot_name,
            icon_emoji=':face_with_head_bandage:'
        )
