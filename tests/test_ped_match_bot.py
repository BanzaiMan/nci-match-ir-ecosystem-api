import unittest
from mock import patch
from ddt import ddt, data, unpack
from common.ped_match_bot import PedMatchBot
import __builtin__
import app


@ddt
@patch('common.ped_match_bot.SlackClient')
class TestPedMatchBot(unittest.TestCase):
    def setUp(self):
        # Starting flask server
        self.app = app.app.test_client()

    @data(
        ('generated_json_message'),
        ('')
    )
    def test_send_message(self, attachments, mock_slack):
        instance = mock_slack.return_value
        instance.api_call.return_value = True

        return_value = PedMatchBot.send_message(attachments)

        print return_value

        self.assertTrue(mock_slack.called)

    @data(
        ('generated_json_message', 'task_id'),
        ('', 'task_id2')
    )
    @unpack
    def test_upload_to_slack(self, message, id, mock_slack):
        instance = mock_slack.return_value
        instance.api_call.return_value = True

        return_value = PedMatchBot.upload_to_slack(message, id)

        print return_value

        self.assertTrue(mock_slack.called)
        self.assertTrue(mock_slack.return_value)

    @patch('common.ped_match_bot.inspect')
    def test_generate_traceback_message(self, mock_inspection, mock_slack):
        instance = mock_slack.return_value
        instance.api_call.return_value = True

        instance2 = mock_inspection.return_value
        instance.f_locals.return_value = True

        stack = instance2

        return_value = PedMatchBot.generate_traceback_message(stack)

        print return_value

        self.assertTrue(mock_inspection.return_value)


    if __name__ == "__main__":
        unittest.main()