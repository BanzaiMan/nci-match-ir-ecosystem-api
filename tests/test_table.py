from unittest import TestCase
import app
import json
from ddt import ddt, data, unpack
from mock import patch

@ddt
class TestTable(TestCase):
    def setUp(self):
        # Starting flask server
        self.app = app.app.test_client()

    @data(
        ([{"site": "mocha", "control_type": "no_template",
           "date_molecular_id_created": "2016-08-18 19:56:19.766",
           "molecular_id": "SC_SA1CB", "ion_reporter_id": "IR_WAO85"}], '', 200),
        (None, '?site=brent', 404),
        ([], '', 200)
    )
    @unpack
    @patch('resources.table.Table')
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
