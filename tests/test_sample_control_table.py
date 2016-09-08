import unittest
import app
from ddt import ddt, data, unpack
from mock import patch, MagicMock


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
        print return_value.status_code
        assert return_value.status_code == expected_results
        if expected_results == 200:
            assert len(return_value.data) > 0
        else:
            print "Return value: " + return_value.data
            assert return_value.data.startswith('{"message": "No sample controls meet the query parameters.')

    @data(('/SC_SA1CB', 200))
    @unpack
    @patch('accessors.celery_task_accessor.CeleryTaskAccessor.delete_items')
    def test_delete(self, parameters, expected_results, mock_delete_items_method):
        mock_delete_items_method.return_value = ('{"message": "Sample control with molecular id:' + parameters)
        return_value = self.app.delete('/api/v1/sample_controls' + parameters)
        print return_value.status_code
        assert return_value.status_code == expected_results

if __name__ == '__main__':
    unittest.main()
