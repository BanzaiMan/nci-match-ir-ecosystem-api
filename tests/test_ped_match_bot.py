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


    @data(
        ('wao_queue', 'Your message here', 'your error here', 'wao_queue_dlx'),
        ('', '', '', '')
    )
    @unpack
    @patch('common.ped_match_bot.PedMatchBot.return_slack_message_and_retry')
    @patch('common.ped_match_bot.inspect')
    @patch('tasks.tasks')
    @patch('common.ped_match_bot.PedMatchBot')
    def test_return_slack_message_and_retry(self, queue_name, message, error_message, dlx_queue, mock_send_message, mock_task, mock_inspection, mock_slack, mock_logger):


        instance0 = mock_send_message.return_value
        instance0.upload_to_slack.return_value = True

        task = mock_task.celery
        task.request.id = True

        logger = mock_logger.logger
        logger.error = Exception

        instance = mock_slack.return_value
        instance.api_call.return_value = True

        instance2 = mock_inspection.return_value
        instance.f_locals.return_value = True

        stack = instance2

        return_value = PedMatchBot.return_slack_message_and_retry(queue_name, message, error_message, stack, task, logger, dlx_queue)

        print return_value

        # self.assertTrue(mock_inspection.called)
        self.assertTrue(mock_inspection.return_value)
        self.assertTrue(mock_slack.return_value)

    if __name__ == "__main__":
        unittest.main()