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
             "ion_reporter_id": "IR_WAO85",
             "site": "mocha"
         },
         'SC_YQ111', 404, {}, 200, "sample_control"),
        ({}, 'SC_YQ999', 404, {}, 404, None),
        ({},
         'PT_SR10_BdVRRejected_BD_MOI1',
         200,
         {
             "uuid": "69cf6ae8-d95b-463a-be4e-1ba2b7ebdf04",
             "shipped_date": "2016-05-01T19:42:13+00:00",
             "patient_id": "PT_SR10_BdVRRejected",
             "molecular_id": "PT_SR10_BdVRRejected_BD_MOI1",
             "study_id": "APEC1621",
             "type": "BLOOD_DNA",
             "carrier": "Federal Express",
             "tracking_id": "7956 4568 1235",
             "destination": "MDA",
             "dna_volume_ul": "10.0",
             "dna_concentration_ng_per_ul": "25.0",
             "cdna_volume_ul": "10.0"
         },
         200, "patient")
    )
    @unpack
    @patch('resources.aliquot.PatientEcosystemConnector')
    @patch('resources.aliquot.SampleControlAccessor')
    def test_get(self, item, molecular_id, verify_pt_status_code, pt_item,
                 expected_results, expected_molecular_id_type, mock_SC_class,  mock_pt_connector_class):
        instance = mock_SC_class.return_value
        instance.get_item.return_value = item
        instance_pt = mock_pt_connector_class.return_value
        instance_pt.verify_molecular_id.return_value = (verify_pt_status_code, pt_item)
        return_value = self.app.get('/api/v1/aliquot/' + molecular_id)
        print "==============" + str(return_value.status_code)
        assert return_value.status_code == expected_results
        if return_value.status_code == 200:
            print json.loads(return_value.data)['molecular_id_type']
            assert json.loads(return_value.data)['molecular_id_type'] == expected_molecular_id_type

    @data(
        ('SC_5AMCC',
         {"vcf_name": "mocha/SC_5AMCC/SC_5AMCC_SC_5AMCC_k123_v1/SC_5AMCC_SC_5AMCC_analysis667_v1.vcf",
          "dna_bam_name": "mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_DNA_v2.bam",
          "cdna_bam_name": "mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam",
          "qc_name": "mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_v2_QC.pdf",
          "site": "mocha",
          "molecular_id": "SC_5AMCC",
          "ion_reporter_id": "IR_WAO85",
          "analysis_id": "SC_5AMCC_SC_5AMCC_k123_v1"
         },
         True,
         {"molecular_id_type": "sample_control", "site_ip_address": "129.43.127.134", "control_type": "positive",
          "molecular_id": "SC_5AMCC"},
         404, {}, 'Item updated'
        ),
        ('SC_5AMCC',
         {"report_status": "PASS",
          "molecular_id": "SC_5AMCC",
          "ion_reporter_id": "IR_WAO85",
          "analysis_id": "SC_5AMCC_SC_5AMCC_k123_v1"
          },
         True,
         {"molecular_id_type": "sample_control", "site_ip_address": "129.43.127.134", "control_type": "positive",
          "molecular_id": "SC_5AMCC"},
         404, {}, 'Item updated'
         ),
        ('SC_5AMCC',
         {"confirmed": False,
          "molecular_id": "SC_5AMCC",
          "ion_reporter_id": "IR_WAO85",
          "analysis_id": "SC_5AMCC_SC_5AMCC_k123_v1"
          },
         True,
         {"molecular_id_type": "sample_control", "site_ip_address": "129.43.127.134", "control_type": "positive",
          "molecular_id": "SC_5AMCC"},
         404, {}, 'Item updated'
         ),
        ( 'PT_SR10_BdVRRejected_BD_MOI1',
          {
            "ion_reporter_id": "IR_WAO85",
            "analysis_id": "job2",
            "site": "mocha",
            "vcf_name": "IR_WAO85/PT_SR10_BdVRRejected_BD_MOI1/job2/3366.vcf",
            "dna_bam_name": "IR_WAO85/PT_SR10_BdVRRejected_BD_MOI1/job2/dna.bam",
            "cdna_bam_name": "IR_WAO85/PT_SR10_BdVRRejected_BD_MOI1/job2/cdna.bam",
            "qc_name": "IR_WAO85/PT_SR10_BdVRRejected_BD_MOI1/job2/qc.pdf"
          },
          True, {}, 200,
          {
              "uuid": "69cf6ae8-d95b-463a-be4e-1ba2b7ebdf04",
              "shipped_date": "2016-05-01T19:42:13+00:00",
              "patient_id": "PT_SR10_BdVRRejected",
              "molecular_id": "PT_SR10_BdVRRejected_BD_MOI1",
              "study_id": "APEC1621",
              "type": "BLOOD_DNA",
              "carrier": "Federal Express",
              "tracking_id": "7956 4568 1235",
              "destination": "MDA",
              "dna_volume_ul": "10.0",
              "dna_concentration_ng_per_ul": "25.0",
              "cdna_volume_ul": "10.0"
          }, 'Item updated'
        ),
        ('SC_YQ111', {}, False, {}, 404, {}, 'Need to pass in item updating information in order to update a sample control item')
    )
    @unpack
    @patch('resources.aliquot.PatientEcosystemConnector')
    @patch('resources.aliquot.SampleControlAccessor')
    @patch('resources.aliquot.DictionaryHelper.has_values')
    @patch('resources.aliquot.CeleryTaskAccessor')
    def test_put(self, molecular_id, update_dictionary, dict_has_value, sc_get_return, verify_pt_statuscode, verify_pt_data,
                 expected_results, mock_celery_task_accessor_class, mock_has_values_function, mock_sc_class, mock_pt_connector_class):
        instance = mock_celery_task_accessor_class.return_value
        instance.process_file.return_value = True
        instance_sc = mock_sc_class.return_value
        instance_sc.get_item.return_value = sc_get_return
        instance_pt = mock_pt_connector_class.return_value
        instance_pt.verify_molecular_id.return_value = (verify_pt_statuscode, verify_pt_data)
        mock_has_values_function.return_value = dict_has_value

        return_value = self.app.put('/api/v1/aliquot/' + molecular_id,
                                    data=json.dumps(update_dictionary),
                                    content_type='application/json')
        print return_value.status_code
        print "=====================?" + str(return_value.data)
        assert expected_results in return_value.data

    @data(
        ('SC_YQ111',
         {  "vcf_name": "mocha/SC_5AMCC/SC_5AMCC_SC_5AMCC_k123_v1/SC_5AMCC_SC_5AMCC_analysis667_v1.vcf",
            "dna_bam_name": "mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_DNA_v2.bam",
            "cdna_bam_name": "mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam",
            "qc_name": "mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_v2_QC.pdf",
            "site": "mocha",
            "molecular_id": "SC_YQ111",
            "ion_reporter_id": "IR_WAO85",
            "analysis_id": "SC_5AMCC_SC_5AMCC_k123_v1"
         },
         {}, 404, {'message': 'Resource not found'}, 'SC_YQ111 was not found.')
    )
    @unpack
    @patch('resources.aliquot.PatientEcosystemConnector')
    @patch('resources.aliquot.SampleControlAccessor')
    @patch('resources.aliquot.DictionaryHelper.has_values')
    @patch('resources.aliquot.CeleryTaskAccessor')
    def test_put_exception(self, molecular_id, update_dictionary, sc_get_return, verify_pt_statuscode, verify_pt_data,
                           exception_message, mock_celery_task_accessor_class, mock_has_values_function, mock_sc_class, mock_pt_connector_class):
        instance = mock_celery_task_accessor_class.return_value
        instance.process_file.return_value = False
        mock_has_values_function.return_value = True
        instance_sc = mock_sc_class.return_value
        instance_sc.get_item.return_value = sc_get_return
        instance_pt = mock_pt_connector_class.return_value
        instance_pt.verify_molecular_id.return_value = (verify_pt_statuscode, verify_pt_data)

        return_value = self.app.put('/api/v1/aliquot/' + molecular_id,
                                    data=json.dumps(update_dictionary),
                                    content_type='application/json')
        print return_value.status_code
        print return_value.data
        assert return_value.status_code == 404
        assert exception_message in return_value.data

    @data(
        ('SC_5AMCC',
         {"vcf_name": "mocha/SC_5AMCC/SC_5AMCC_SC_5AMCC_k123_v1/SC_5AMCC_SC_5AMCC_analysis667_v1.vcf",
          "molecular_id": "SC_5AMCC", "analysis_id": "SC_5AMCC_SC_5AMCC_k123_v1", "ion_reporter_id": "IR_WAO85"},
         {"molecular_id_type": "sample_control", "site_ip_address": "129.43.127.134", "control_type": "positive",
          "molecular_id": "SC_5AMCC"},
          404, {'message': 'Resource not found'}, ' Testing put process_file exception')
    )
    @unpack
    @patch('common.ped_match_bot.PedMatchBot.send_message')
    @patch('resources.aliquot.PatientEcosystemConnector')
    @patch('resources.aliquot.SampleControlAccessor')
    @patch('resources.aliquot.DictionaryHelper.has_values')
    @patch('resources.aliquot.CeleryTaskAccessor')
    def test_put_process_file_exception(self, molecular_id, update_dictionary, sc_get_return, verify_pt_statuscode,
                                        verify_pt_data, exception_message, mock_celery_task_accessor_class,
                                        mock_has_values_function, mock_sc_class, mock_pt_connector_class, mock_log_abort):
        instance = mock_celery_task_accessor_class.return_value
        instance.process_file.side_effect = Exception(exception_message)
        mock_has_values_function.return_value = True
        mock_log_abort.return_value = True
        instance_sc = mock_sc_class.return_value
        instance_sc.get_item.return_value = sc_get_return
        instance_pt = mock_pt_connector_class.return_value
        instance_pt.verify_molecular_id.return_value = (verify_pt_statuscode, verify_pt_data)

        return_value = self.app.put('/api/v1/aliquot/' + molecular_id,
                                    data=json.dumps(update_dictionary),
                                    content_type='application/json')
        print "-----------------" + str(return_value.status_code)
        print return_value.data
        print return_value.status_code
        assert return_value.status_code == 500
        assert exception_message in return_value.data

    @data(
        ('SC_5AMCC',
         {"vgg_name": "mocha/SC_5AMCC/SC_5AMCC_SC_5AMCC_k123_v1/SC_5AMCC_SC_5AMCC_analysis667_v1.vcf", "site": "mocha",
          "molecular_id": "SC_5AMCC", "analysis_id": "SC_5AMCC_SC_5AMCC_k123_v1", "ion_reporter_id": "IR_WAO85"},
         {"molecular_id_type": "sample_control", "site_ip_address": "129.43.127.134", "control_type": "positive",
          "molecular_id": "SC_5AMCC"},
         404, {'message': 'Resource not found'}, 400)
    )
    @unpack
    @patch('resources.aliquot.PatientEcosystemConnector')
    @patch('resources.aliquot.SampleControlAccessor')
    @patch('resources.aliquot.DictionaryHelper.has_values')
    @patch('resources.aliquot.CeleryTaskAccessor')
    def test_put_distinct_tasks_list_exception(self, molecular_id, update_dictionary, sc_get_return, verify_pt_statuscode,
                                               verify_pt_data, result_status_code, mock_celery_task_accessor_class,
                                               mock_has_values_function, mock_sc_class, mock_pt_connector_class):
        instance = mock_celery_task_accessor_class.return_value
        instance.process_file.return_value = True
        mock_has_values_function.return_value = True
        instance_sc = mock_sc_class.return_value
        instance_sc.get_item.return_value = sc_get_return
        instance_pt = mock_pt_connector_class.return_value
        instance_pt.verify_molecular_id.return_value = (verify_pt_statuscode, verify_pt_data)

        return_value = self.app.put('/api/v1/aliquot/' + molecular_id,
                                    data=json.dumps(update_dictionary),
                                    content_type='application/json')

        print "-----------------" + str(return_value.status_code)
        print return_value.data
        assert return_value.status_code == result_status_code

# if __name__ == '__main__':
#     unittest.main()
