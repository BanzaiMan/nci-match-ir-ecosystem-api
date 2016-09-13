import unittest
import app
import json
from ddt import ddt, data, unpack
from mock import patch, MagicMock, Mock


@ddt
class TestIonReporterTable(unittest.TestCase):
    def setUp(self):
        # Starting flask server
        self.app = app.app.test_client()

    @data(([{"site": "mocha", "host_name": "NCI-MATCH-IR",
             "status": "Contacted 4 minutes ago",
             "last_contact": "August 29, 2016 2:01 PM GMT", "ion_reporter_id": "IR_WAO85"}], '', 200),
          (None, '?site=brent', 404))
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
            assert return_value.data.startswith('{"message": "No ion reporters meet the query parameters.')

    @patch('resources.ion_reporter_table.IonReporterAccessor')
    def test_get_exception(self, mock_class):
        instance = mock_class.return_value
        instance.scan.side_effect = Exception('testing throwing exception')
        return_value = self.app.get('/api/v1/ion_reporters')
        assert return_value.status_code == 500
        assert "testing throwing exception" in return_value.data

    @data(('?site=mocha', '{"result": "Batch deletion request placed on queue to be processed"}'),
          ('', '{"message": "Cannot use batch delete to delete all records.'))
    @unpack
    @patch('resources.ion_reporter_table.CeleryTaskAccessor')
    def test_delete(self, parameters, expected_results, mock_class):
        instance = mock_class.return_value
        instance.delete_ir_items.return_value = True
        return_value = self.app.delete('/api/v1/ion_reporters' + parameters)
        assert expected_results in return_value.data

    @patch('resources.ion_reporter_table.CeleryTaskAccessor')
    def test_delete_exception(self, mock_class):
        instance = mock_class.return_value
        instance.delete_ir_items.side_effect = Exception('testing throwing exception')
        return_value = self.app.delete('/api/v1/ion_reporters?site=mocha')
        assert "testing throwing exception" in return_value.data
        assert return_value.status_code == 500

    @data(('?site=mocha',
           '{"result": "New ion reporter created", "ion_reporter_id":'),
          ('', '{"message": "Must send in a site in order to create an ion reporter record"}'),
          ('?ion_reporter_id=IR_WAO85', 'failed, because ion_reporter_id'))
    @unpack
    @patch('resources.ion_reporter_table.IonReporterAccessor')
    def test_post(self, parameters, expected_results, mock_class):
        instance = mock_class.return_value
        instance.get_unique_key.return_value = 'IR_WAO85'
        return_value = self.app.post('/api/v1/ion_reporters' + parameters)
        assert expected_results in return_value.data

    @patch('resources.ion_reporter_table.IonReporterAccessor')
    def test_post_exception(self, mock_class):
        instance = mock_class.return_value
        instance.put_item.side_effect = Exception('Ion reporter creation failed')
        return_value = self.app.post('/api/v1/ion_reporters?site=mocha')
        assert return_value.status_code == 500
        assert "Ion reporter creation failed" in return_value.data


if __name__ == '__main__':
    unittest.main()
