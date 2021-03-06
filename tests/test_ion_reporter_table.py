from mock import patch
patch('resources.auth0_resource.requires_auth', lambda x: x).start()
import unittest
import app
import json
from ddt import ddt, data, unpack


@ddt
class TestIonReporterTable(unittest.TestCase):
    def setUp(self):
        # Starting flask server
        self.app = app.app.test_client()

    @data(
        ([{"site": "mocha", "host_name": "NCI-MATCH-IR",
           "status": "Contacted 4 minutes ago",
           "last_contact": "August 29, 2016 2:01 PM GMT", "ion_reporter_id": "IR_WAO85"}], '', 200),
        (None, '?site=brent', 404),
        ([], '', 404)
    )
    @unpack
    @patch('resources.ion_reporter_table.IonReporterAccessor')
    def test_get(self, database_data, parameters, expected_results, mock_class):
        instance = mock_class.return_value
        instance.scan.return_value = database_data
        return_value = self.app.get('/api/v1/ion_reporters' + parameters)
        assert return_value.status_code == expected_results
        if expected_results == 200:
            assert len(return_value.data) > 0
            assert (json.loads(return_value.data))[0]['site'] == "mocha"
        else:
            assert return_value.data.startswith('{"message": "No records meet the query parameters')

    @patch('common.ped_match_bot.PedMatchBot.send_message')
    @patch('resources.ion_reporter_table.IonReporterAccessor')
    def test_get_exception(self, mock_class, mock_log_abort):
        mock_log_abort.return_value = True
        instance = mock_class.return_value
        instance.scan.side_effect = Exception('testing throwing exception')
        return_value = self.app.get('/api/v1/ion_reporters')
        assert return_value.status_code == 500
        assert "testing throwing exception" in return_value.data

    @data(('?site=mocha', '"result": "Batch deletion request placed on queue to be processed"'),
          ('', '{"message": "Cannot use batch delete to delete all records.'))
    @unpack
    @patch('resources.ion_reporter_table.CeleryTaskAccessor')
    def test_delete(self, parameters, expected_results, mock_class):
        instance = mock_class.return_value
        instance.delete_ir_items.return_value = True
        return_value = self.app.delete('/api/v1/ion_reporters' + parameters)
        print return_value.data

        assert expected_results in return_value.data

    @patch('common.ped_match_bot.PedMatchBot.send_message')
    @patch('resources.ion_reporter_table.CeleryTaskAccessor')
    def test_delete_exception(self, mock_class, mock_log_abort):
        mock_log_abort.return_value = True
        instance = mock_class.return_value
        instance.delete_ir_items.side_effect = Exception('No items with query parameters')
        return_value = self.app.delete('/api/v1/ion_reporters?site=mocha')
        assert "No items with query parameters" in return_value.data
        assert return_value.status_code == 500

    @data(
        ('?site=mocha',
           "New ion reporter created"),
          ('', 'Ion reporter creation failed, because site was not passed in.'),
          ('?ion_reporter_id=IR_WAO85', 'failed, because ion_reporter_id')
    )
    @unpack
    @patch('resources.ion_reporter_table.IonReporterAccessor')
    def test_post(self, parameters, expected_results, mock_class):
        instance = mock_class.return_value
        instance.get_unique_key.return_value = 'IR_WAO85'
        return_value = self.app.post('/api/v1/ion_reporters' + parameters)
        print return_value.data
        assert expected_results in return_value.data

    @patch('common.ped_match_bot.PedMatchBot.send_message')
    @patch('resources.ion_reporter_table.IonReporterAccessor')
    def test_post_exception(self, mock_class, mock_log_abort):
        mock_log_abort.return_value = True
        instance = mock_class.return_value
        instance.put_item.side_effect = Exception('Ion reporter creation failed')
        return_value = self.app.post('/api/v1/ion_reporters?site=mocha')
        assert return_value.status_code == 500
        assert "Ion reporter creation failed" in return_value.data


# # if __name__ == '__main__':
# #     unittest.main()
