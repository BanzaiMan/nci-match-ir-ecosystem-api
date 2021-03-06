from mock import patch
patch('resources.auth0_resource.requires_auth', lambda x: x).start()
import unittest
import app
import json
from ddt import ddt, data, unpack



@ddt
class TestSampleControlTable(unittest.TestCase):
    def setUp(self):
        # Starting flask server
        self.app = app.app.test_client()

    @data(
        ([{"site": "mocha", "control_type": "no_template",
           "date_molecular_id_created": "2016-08-18 19:56:19.766",
           "molecular_id": "SC_SA1CB", "ion_reporter_id": "IR_WAO85"}], '', 200),
        (None, '?site=brent', 404),
        ([], '', 404)
    )
    @unpack
    @patch('resources.sample_control_table.SampleControlAccessor')
    def test_get(self, database_data, parameters, expected_results, mock_class):
        instance = mock_class.return_value
        instance.scan.return_value = database_data
        return_value = self.app.get('/api/v1/sample_controls' + parameters)
        assert return_value.status_code == expected_results
        if expected_results == 200:
            assert len(return_value.data) > 0
            assert (json.loads(return_value.data))[0]['site'] == "mocha"
        else:
            assert return_value.data.startswith('{"message": "No records meet the query parameters')

    @patch('common.ped_match_bot.PedMatchBot.send_message')
    @patch('resources.sample_control_table.SampleControlAccessor')
    def test_get_exception(self, mock_class, mock_log_abort):
        mock_log_abort.return_value = True
        instance = mock_class.return_value
        instance.scan.side_effect = Exception('testing throwing exception')
        return_value = self.app.get('/api/v1/sample_controls')
        assert return_value.status_code == 500
        assert "testing throwing exception" in return_value.data

    @data(
        ('?site=mocha', "Batch deletion request placed on queue to be processed"),
        ('', 'Cannot use batch delete to delete all records.')
    )
    @unpack
    @patch('resources.sample_control_table.CeleryTaskAccessor')
    def test_delete(self, parameters, expected_results, mock_class):
        instance = mock_class.return_value
        instance.delete_items.return_value = True
        return_value = self.app.delete('/api/v1/sample_controls' + parameters)
        print return_value.data
        assert expected_results in str(return_value.data)

    @patch('common.ped_match_bot.PedMatchBot.send_message')
    @patch('resources.sample_control_table.CeleryTaskAccessor')
    def test_delete_exception(self, mock_class, mock_log_abort):
        mock_log_abort.return_value = True
        instance = mock_class.return_value
        instance.delete_items.side_effect = Exception('testing throwing exception')
        return_value = self.app.delete('/api/v1/sample_controls?site=mocha')
        assert "testing throwing exception" in return_value.data
        assert return_value.status_code == 500

    @data(
        ('?site=mocha&control_type=no_template', '"New sample control created"'),
        ('?site=mocha', '{"message": "Sample Control creation failed, because both '
                        'site and control_type were not passed in"}'),
        ('?control_type=no_template', '{"message": "Sample Control creation failed, because both '
                                      'site and control_type were not passed in"}'),
        ('', '{"message": "Sample Control creation failed, because both '
             'site and control_type were not passed in"}'),
        ('?molecular_id=SC_WAO85', 'failed, because molecular_id')
    )
    @unpack
    @patch('resources.sample_control_table.SampleControlAccessor')
    def test_post(self, parameters, expected_results, mock_key):
        mock_key.put_item.return_value = 'SC_WAO85'
        return_value = self.app.post('/api/v1/sample_controls' + parameters)
        print return_value.data
        assert expected_results in return_value.data

    @patch('common.ped_match_bot.PedMatchBot.send_message')
    @patch('resources.sample_control_table.SampleControlAccessor')
    def test_post_exception(self, mock_class, mock_log_abort):
        mock_log_abort.return_value = True
        instance = mock_class.return_value
        instance.put_item.side_effect = Exception('Sample Control creation failed')
        return_value = self.app.post('/api/v1/sample_controls?site=mocha&control_type=no_template')
        assert return_value.status_code == 500
        assert "Sample Control creation failed" in return_value.data
#

# # # if __name__ == '__main__':
# # #     unittest.main()
