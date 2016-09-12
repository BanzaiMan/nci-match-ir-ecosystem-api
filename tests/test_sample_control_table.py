import unittest
import sys
sys.path.append("..")
import app
import json
from ddt import ddt, data, unpack
from mock import patch, MagicMock, Mock


@ddt
class TestSampleControlTable(unittest.TestCase):
    def setUp(self):
        # Starting flask server
        self.app = app.app.test_client()

    @data(([{"site": "mocha", "control_type": "no_template",
             "date_molecular_id_created": "2016-08-18 19:56:19.766",
             "molecular_id": "SC_SA1CB", "ion_reporter_id": "IR_WAO85"}], '', 200),
          (None, '?site=brent', 404))
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
            assert return_value.data.startswith('{"message": "No sample controls meet the query parameters.')

    @patch('accessors.sample_control_accessor.SampleControlAccessor.scan')
    def test_get_exception(self, mock_scan_method):
        mock_scan_method.side_effect = Exception('testing throwing exception')
        return_value = self.app.get('/api/v1/sample_controls')
        assert return_value.status_code == 500
        assert "testing throwing exception" in return_value.data

    @data(('?site=mocha', '{"result": "Batch deletion request placed on queue to be processed"}'),
          ('', '{"message": "Cannot use batch delete to delete all records.'))
    @unpack
    @patch('accessors.celery_task_accessor.CeleryTaskAccessor.delete_items')
    def test_delete(self, parameters, expected_results, mock_delete_items_method):
        mock_delete_items_method.return_value = True
        return_value = self.app.delete('/api/v1/sample_controls' + parameters)
        assert return_value.data.startswith(expected_results)

    @patch('accessors.celery_task_accessor.CeleryTaskAccessor.delete_items')
    def test_delete_exception(self, mock_delete_items_method):
        mock_delete_items_method.side_effect = Exception('testing throwing exception')
        return_value = self.app.delete('/api/v1/sample_controls?site=mocha')
        assert "testing throwing exception" in return_value.data
        assert return_value.status_code == 500

    @data(('?site=mocha&control_type=no_template',
           '{"result": "New sample control created", "molecular_id":'),
          ('?site=mocha', '{"message": "Sample Control creation failed, because both '
                     'site and control_type were not passed in"}'),
          ('?control_type=no_template', '{"message": "Sample Control creation failed, because both '
                     'site and control_type were not passed in"}'),
          ('', '{"message": "Sample Control creation failed, because both '
                     'site and control_type were not passed in"}'),
          ('?molecular_id=SC_WAO85', 'failed, because molecular_id'))
    @unpack
    @patch('resources.sample_control_table.SampleControlTable.get_unique_key')
    @patch('accessors.sample_control_accessor.SampleControlAccessor.put_item')
    def test_post(self, parameters, expected_results, mock_put_item_method, mock_get_unique_key):
        mock_put_item_method.return_value = True
        mock_get_unique_key.return_value = 'SC_WAO85'
        return_value = self.app.post('/api/v1/sample_controls' + parameters)
        assert expected_results in return_value.data

    @patch('accessors.sample_control_accessor.SampleControlAccessor.put_item')
    def test_post_exception(self, mock_put_item_method):
        mock_put_item_method.side_effect = Exception('Sample Control creation failed')
        return_value = self.app.post('/api/v1/sample_controls?site=mocha&control_type=no_template')
        assert return_value.status_code == 500
        assert "Sample Control creation failed" in return_value.data

if __name__ == '__main__':
    unittest.main()
