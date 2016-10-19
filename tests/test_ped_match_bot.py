import unittest
from unittest import TestCase
from mock import patch
from ddt import ddt, data, unpack
from common.ped_match_bot import PedMatchBot
from mock import patch
import __builtin__


@ddt
class TestPedMatchBot(TestCase):

    def setUp(self):

        self.ped_match_bot = PedMatchBot()
        pass

    @data(
        ('C2NEK70F9', 'Your message here.')
    )
    @unpack
    @patch('common.ped_match_bot.slack_client.api_call')
    def test_send_message(self, channel_id, message, mock_slack):
        mock_slack.return_value = True
        return_value = PedMatchBot.send_message(channel_id, message)
        print return_value

        self.assertTrue(mock_slack.called)

    if __name__ == "__main__":
        unittest.main()