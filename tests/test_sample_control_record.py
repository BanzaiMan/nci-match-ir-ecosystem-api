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
            ({"site_ip_address": "129.43.127.133", "control_type": "no_template", "dna_bam_name": "mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_DNA_v2.bam", "site": "mocha", "qc_name": "None", "dna_bai_name": "mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_DNA_v2.bai", "tsv_name": "mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_v2.tsv", "cdna_bam_name": "mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam", "vcf_name": "mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_v2.vcf", "cdna_bai_name": "mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bai", "date_molecular_id_created": "2016-08-28 16:56:29.333", "molecular_id": "SC_YQ111", "analysis_id": "SC_YQ111_SC_YQ111_k123_v1"}, 'SC_YQ111', 200),
            ({}, 'SC_YQ999', 404)
    )
    @unpack
    @patch('accessors.sample_control_accessor.SampleControlAccessor')
    def test_get(self, item, molecular_id, expected_results, mock_scAccessor_class):
        instance = mock_scAccessor_class.return_value
        instance.get_item.return_value = item
        return_value = self.app.get('/api/v1/sample_controls/' + molecular_id)
        assert return_value.status_code == expected_results
        if expected_results == 200:
            assert len(return_value.data) > 0
            assert (json.loads(return_value.data))['site'] == "mocha"
        else:
            print return_value.data
            assert return_value.data.find("message")

    @data(
        ('SC_5AMCC', '"message": "Item deleted"')
    )
    @unpack
    @patch('accessors.celery_task_accessor.CeleryTaskAccessor.delete_item')
    def test_delete(self, molecular_id, expected_results, mock_delete_item_method):
        mock_delete_item_method.return_value = True
        return_value = self.app.delete('/api/v1/sample_controls/' + molecular_id)
        print "return data=" + str(return_value.data)
        assert return_value.data.find(expected_results)

    @data(
        ('SC_5AMCC',
         {'vcf_name': 'mocha/SC_5AMCC/SC_5AMCC_SC_5AMCC_k123_v1/SC_5AMCC_SC_5AMCC_analysis667_v1.vcf', 'site': 'mocha',
          'molecular_id': 'SC_5AMCC', 'analysis_id': 'SC_5AMCC_SC_5AMCC_k123_v1'}, '"message"')
    )
    @unpack
    @patch('accessors.celery_task_accessor.CeleryTaskAccessor.update_item')
    def test_put(self, molecular_id, update_dictionary, expected_results, mock_update_item_method):
        mock_update_item_method.return_value = True
        return_value = self.app.put('/api/v1/aliquot/' + molecular_id,
                                    data=update_dictionary,
                                    headers={'Content-Type': 'application/json'})
        assert return_value.data.find(expected_results)

if __name__ == '__main__':
    unittest.main()