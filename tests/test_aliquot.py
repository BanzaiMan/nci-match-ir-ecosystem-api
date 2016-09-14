import unittest
import json
from ddt import ddt, data, unpack
from mock import patch
import sys
sys.path.append("..")
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
         },
         'SC_YQ111', 200),
        ({}, 'SC_YQ999', 404)
    )
    @unpack
    @patch('resources.aliquot.SampleControlAccessor')
    def test_get(self, item, molecular_id, expected_results, mock_aliquot_class):
        instance = mock_aliquot_class.return_value
        instance.get_item.return_value = item
        return_value = self.app.get('/api/v1/aliquot/' + molecular_id)
        print "==============" + str(return_value.status_code)
        assert return_value.status_code == expected_results
        print return_value.data
        if expected_results == 200:
            assert len(return_value.data) > 0
            assert (json.loads(return_value.data))['site'] == "mocha"
        else:
            assert return_value.data.find(molecular_id + " was not found.")


    @data(
        ('SC_5AMCC',
         {'vcf_name': 'mocha/SC_5AMCC/SC_5AMCC_SC_5AMCC_k123_v1/SC_5AMCC_SC_5AMCC_analysis667_v1.vcf', 'site': 'mocha',
          'molecular_id': 'SC_5AMCC', 'analysis_id': 'SC_5AMCC_SC_5AMCC_k123_v1'}, True, 'Item updated'),
        ('SC_YQ111', {}, False, 'message')
    )
    @unpack
    @patch('resources.aliquot.DictionaryHelper')
    @patch('resources.aliquot.CeleryTaskAccessor')
    def test_put(self, molecular_id, update_dictionary, dict_has_value, expected_results, mock_CeleryTaskAccessor_class,
                 mock_DictionaryHelper_class):

        instance = mock_CeleryTaskAccessor_class.return_value
        instance.process_file(update_dictionary).return_value = dict_has_value
        instance2 = mock_DictionaryHelper_class.return_value
        instance2.has_values.return_value = True
        return_value = self.app.put('/api/v1/aliquot/' + molecular_id,
                                    data=json.dumps(update_dictionary),
                                    content_type='application/json')
        print return_value.data
        assert return_value.data.find(expected_results)

if __name__ == '__main__':
    unittest.main()