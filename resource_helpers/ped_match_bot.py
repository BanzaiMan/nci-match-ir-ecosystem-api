import os
import time

from slackclient import SlackClient


BOT_NAME = 'pedmatchbot'
# BOT_ID = os.environ.get("BOT_ID")
BOT_ID = 'U2MUQUA4Q'

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

# slack_client = SlackClient(os.environ.get('SLACK_TOKEN'))
slack_client = SlackClient('xoxb-89976962160-MkbqjjAWHZgU3M343JXLb4r5')

class PedBot(object):



    @staticmethod
    def handle_command(command, channel):
        """
            Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands. If not,
            returns back what it needs for clarification.
        """
        response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
                   "* command with numbers, delimited by spaces."
        if command.startswith(EXAMPLE_COMMAND):
            response = "Sure...write some more code then I can do that!"
        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)

    @staticmethod
    def parse_slack_output(slack_rtm_output):
        """
            The Slack Real Time Messaging API is an events firehose.
            this parsing function returns None unless a message is
            directed at the Bot, based on its ID.
        """
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and AT_BOT in output['text']:
                    # return text after the @ mention, whitespace removed
                    return output['text'].split(AT_BOT)[1].strip().lower(), \
                           output['channel']
        return None, None


    def list_channels(self):
        channels_call = slack_client.api_call("channels.list")
        if channels_call['ok']:
            return channels_call['channels']
        return None


    def channel_info(channel_id):
        channel_info = slack_client.api_call("channels.info", channel=channel_id)
        if channel_info:
            return channel_info['channel']
        return None


    def send_message(self, channel_id, message):
        slack_client.api_call(
            "chat.postMessage",
            channel=channel_id,
            text=message,
            username=BOT_NAME,
            icon_emoji=':face_with_head_bandage:'
        )

    @staticmethod
    def check_for_messages(self):
        READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
        if slack_client.rtm_connect():
            print("PED MATCHBOT connected and running!")
            while True:
                command, channel = self.parse_slack_output(slack_client.rtm_read())
                if command and channel:
                    self.handle_command(command, channel)
                time.sleep(READ_WEBSOCKET_DELAY)
        else:
            print("Connection failed. Invalid Slack token or bot ID?")
