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
    @patch('accessors.ion_reporter_accessor.IonReporterAccessor.scan')
    def test_get(self, database_data, parameters, expected_results, mock_scan_method):
        mock_scan_method.return_value = database_data
        return_value = self.app.get('/api/v1/ion_reporters' + parameters)
        assert return_value.status_code == expected_results
        if expected_results == 200:
            assert len(return_value.data) > 0
            assert (json.loads(return_value.data))[0]['site'] == "mocha"
        else:
            assert return_value.data.startswith('{"message": "No ion reporters meet the query parameters.')

    @patch('accessors.ion_reporter_accessor.IonReporterAccessor.scan')
    def test_get_exception(self, mock_scan_method):
        mock_scan_method.side_effect = Exception('testing throwing exception')
        return_value = self.app.get('/api/v1/ion_reporters')
        assert return_value.status_code == 500
        assert "testing throwing exception" in return_value.data

if __name__ == '__main__':
    unittest.main()
