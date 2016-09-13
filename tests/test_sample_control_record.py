import unittest
import json
from ddt import ddt, data, unpack
from mock import patch, MagicMock, Mock
import sys
sys.path.append("..")
import app

@ddt
class TestSampleControlRecord(unittest.TestCase):
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
    @patch('resources.sample_control_record.SampleControlAccessor')
    def test_get(self, item, molecular_id, expected_results, mock_scRecord_class):
        instance = mock_scRecord_class.return_value
        # instance.SampleControlAccessor.get_item.return_value = item
        instance.get_item.return_value = item
        return_value = self.app.get('/api/v1/sample_controls/' + molecular_id)
        print "==============" + str(return_value.status_code)
        assert return_value.status_code == expected_results
        print return_value.data
        if expected_results == 200:
            assert len(return_value.data) > 0
            assert (json.loads(return_value.data))['site'] == "mocha"
        else:
            print return_value.data
            assert return_value.data.find("message")

    @patch('resources.sample_control_record.SampleControlAccessor')
    def test_get_exception(self, mock_scRecord_class):
        instance = mock_scRecord_class.return_value
        instance.get_item.side_effect = Exception('Testing get_item exception')
        return_value = self.app.get('/api/v1/sample_controls/SC_5AMCC')
        print return_value.status_code
        assert return_value.status_code == 500
        assert "Testing get_item exception" in return_value.data

    @data(
        ('SC_5AMCC', '"message": "Item deleted"')
    )
    @unpack
    @patch('resources.sample_control_record.CeleryTaskAccessor')
    def test_delete(self, molecular_id, expected_results, mock_scRecord_class):
        instance = mock_scRecord_class.return_value
        instance.delete_item.return_value = True
        return_value = self.app.delete('/api/v1/sample_controls/' + molecular_id)
        print "return data=" + str(return_value.data)
        assert return_value.data.find(expected_results)

    @data(
        ('SC_5AMCC',
         {'vcf_name': 'mocha/SC_5AMCC/SC_5AMCC_SC_5AMCC_k123_v1/SC_5AMCC_SC_5AMCC_analysis667_v1.vcf', 'site': 'mocha',
          'molecular_id': 'SC_5AMCC', 'analysis_id': 'SC_5AMCC_SC_5AMCC_k123_v1'}, 'updated')
    )
    @unpack
    @patch('resources.sample_control_record.CeleryTaskAccessor')
    def test_put(self, molecular_id, update_dictionary, expected_results, mock_scRecord_class):
        instance = mock_scRecord_class.return_value
        instance.update_item(update_dictionary).return_value = True
        return_value = self.app.put('/api/v1/sample_controls/' + molecular_id,
                                    data=json.dumps(update_dictionary),
                                    content_type='application/json')
        print return_value.data
        assert return_value.data.find(molecular_id + " " + expected_results)


if __name__ == '__main__':
    unittest.main()