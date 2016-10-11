import os
import time

from slackclient import SlackClient


BOT_NAME = 'pedmatchbot'
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">:"
EXAMPLE_COMMAND = "do"

slack_client = SlackClient(os.environ.get('SLACK_TOKEN'))


if __name__ == "__main__":

    api_call = slack_client.api_call("users.list")
    # print api_call
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
    else:
        print("could not find bot user with the name " + BOT_NAME)


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


    def list_channels():
        channels_call = slack_client.api_call("channels.list")
        if channels_call['ok']:
            return channels_call['channels']
        return None


    def channel_info(channel_id):
        channel_info = slack_client.api_call("channels.info", channel=channel_id)
        if channel_info:
            return channel_info['channel']
        return None


    def send_message(channel_id, message):
        slack_client.api_call(
            "chat.postMessage",
            channel=channel_id,
            text=message,
            username=BOT_NAME,
            icon_emoji=':robot_face:'
        )


    if __name__ == '__main__':
        channels = list_channels()
        if channels:
            print("Channels: ")
            for channel in channels:
                print(channel['name'] + " (" + channel['id'] + ")")
                detailed_info = channel_info(channel['id'])
                if detailed_info:
                    print('Latest text from ' + channel['name'] + ":")
                    print(detailed_info['purpose']['value'])
                if channel['name'] == 'general':
                    send_message(channel['id'], "Hello " +
                                 channel['name'] + "! PEDBOT has initiated.")
            print('-----')
        else:
            print("Unable to authenticate.")

    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")