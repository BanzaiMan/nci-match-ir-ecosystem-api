import unittest
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
    @patch('accessors.sample_control_accessor.SampleControlAccessor.scan')
    def test_get(self, database_data, parameters, expected_results, mock_scan_method):
        mock_scan_method.return_value = database_data
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

    @data(([{"molecular_id": "SC_SA1CB"}],'?site=mocha&control_type=no_template',
           '{"result": "New sample control created", "molecular_id":'),
          (None, '', '{"message": "Sample Control creation failed, because both '
                     'site and control_type were not passed in"}'))
    @unpack
    @patch('accessors.sample_control_accessor.SampleControlAccessor.put_item')
    def test_post(self, database_data, parameters, expected_results, mock_put_item_method):
        mock_put_item_method.return_value = database_data
        return_value = self.app.post('/api/v1/sample_controls' + parameters, content_type='application/json')
        assert return_value.data.startswith(expected_results)


if __name__ == '__main__':
    unittest.main()
