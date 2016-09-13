import unittest
import json
from ddt import ddt, data, unpack
from mock import patch
import app


@ddt
class TestAliquot(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()

    @data(
        ({
             "control_type": "no_template",
             "date_molecular_id_created": "2016-08-28 16:56:29.333",
             "site_ip_address": "129.43.127.133",
             "molecular_id": "SC_YQ111",
             "site": "mocha"
         }, 'SC_YQ111', 200
        ),
        ({}, 'SC_YQ999', 404)
    )
    @unpack
    @patch('resources.aliquot.SampleControlAccessor')
    def test_get(self, item, molecular_id, expected_results, mock_aliquot_class):
        instance = mock_aliquot_class.return_value
        instance.get_item.return_value = item
        return_value = self.app.get('/api/v1/sample_controls/' + molecular_id)
        print "==============" + str(return_value.status_code)
        assert return_value.status_code == expected_results
        print return_value.data
        if expected_results == 200:
            assert len(return_value.data) > 0
            assert (json.loads(return_value.data))['site'] == "mocha"
        else:
            assert return_value.data.find(molecular_id + " was not found.")



if __name__ == '__main__':
    unittest.main()