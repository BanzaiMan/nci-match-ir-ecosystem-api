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
         {'vcf_name': 'mocha/SC_5AMCC/SC_5AMCC_SC_5AMCC_k123_v1/SC_5AMCC_SC_5AMCC_analysis667_v1.vcf',
          'dna_bam_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_DNA_v2.bam',
          'cdna_bam_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam',
          'qc_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_v2_QC.pdf',
          'site': 'mocha',
          'molecular_id': 'SC_5AMCC', 'analysis_id': 'SC_5AMCC_SC_5AMCC_k123_v1'},
         True, 'Item updated'),
        ('SC_YQ111', {}, False, 'Need to pass in item updating information in order to update a sample control item')
    )
    @unpack
    @patch('resources.aliquot.DictionaryHelper.has_values')
    @patch('resources.aliquot.CeleryTaskAccessor')
    @patch('resources.aliquot.reqparse.RequestParser.parse_args')
    def test_put(self, molecular_id, update_dictionary, dict_has_value, expected_results,
                 mock_parse_args_function, mock_celery_task_accessor_class, mock_has_values_function):
        mock_parse_args_function.return_value = update_dictionary
        instance = mock_celery_task_accessor_class.return_value
        instance.process_file.return_value = True
        mock_has_values_function.return_value = dict_has_value
        return_value = self.app.put('/api/v1/aliquot/' + molecular_id,
                                    data=json.dumps(update_dictionary),
                                    content_type='application/json')
        print return_value.data
        assert expected_results in return_value.data

    @data(
        ('SC_YQ111', {}, 'Need to pass in item updating information in order to update a sample control item.')
    )
    @unpack
    @patch('resources.aliquot.DictionaryHelper.has_values')
    @patch('resources.aliquot.CeleryTaskAccessor')
    @patch('resources.aliquot.reqparse.RequestParser.parse_args')
    def test_put_exception(self, molecular_id, update_dictionary, exception_message,
                           mock_parse_args_function, mock_celery_task_accessor_class, mock_has_values_function):
        mock_parse_args_function.return_value = update_dictionary
        instance = mock_celery_task_accessor_class.return_value
        instance.process_file.return_value = False
        mock_has_values_function.return_value = False

        return_value = self.app.put('/api/v1/aliquot/' + molecular_id,
                                    data=json.dumps(update_dictionary),
                                    content_type='application/json')
        print return_value.status_code
        print return_value.data
        assert return_value.status_code == 400
        assert exception_message in return_value.data

    @data(
        ('SC_5AMCC',
         {'vcf_name': 'mocha/SC_5AMCC/SC_5AMCC_SC_5AMCC_k123_v1/SC_5AMCC_SC_5AMCC_analysis667_v1.vcf', 'site': 'mocha',
          'molecular_id': 'SC_5AMCC', 'analysis_id': 'SC_5AMCC_SC_5AMCC_k123_v1'},
         ' Testing put process_file exception')
    )
    @unpack
    @patch('resources.aliquot.DictionaryHelper.has_values')
    @patch('resources.aliquot.CeleryTaskAccessor')
    @patch('resources.aliquot.reqparse.RequestParser.parse_args')
    def test_put_process_file_exception(self, molecular_id, update_dictionary, exception_message,
                                        mock_parse_args_function, mock_celery_task_accessor_class,
                                        mock_has_values_function):
        mock_parse_args_function.return_value = update_dictionary
        instance = mock_celery_task_accessor_class.return_value
        instance.process_file.side_effect = Exception(exception_message)
        mock_has_values_function.return_value = True

        return_value = self.app.put('/api/v1/aliquot/' + molecular_id,
                                    data=json.dumps(update_dictionary),
                                    content_type='application/json')
        print "-----------------" + str(return_value.status_code)
        print return_value.data
        assert return_value.status_code == 500
        assert exception_message in return_value.data

    @data(
        ('SC_5AMCC',
         {'vgg_name': 'mocha/SC_5AMCC/SC_5AMCC_SC_5AMCC_k123_v1/SC_5AMCC_SC_5AMCC_analysis667_v1.vcf', 'site': 'mocha',
          'molecular_id': 'SC_5AMCC', 'analysis_id': 'SC_5AMCC_SC_5AMCC_k123_v1'},
         'No distinct tasks where found in message')
    )
    @unpack
    @patch('resources.aliquot.DictionaryHelper.has_values')
    @patch('resources.aliquot.CeleryTaskAccessor')
    @patch('resources.aliquot.reqparse.RequestParser.parse_args')
    def test_put_distinct_tasks_list_exception(self, molecular_id, update_dictionary, exception_message,
                                               mock_parse_args_function, mock_celery_task_accessor_class,
                                               mock_has_values_function):
        mock_parse_args_function.return_value = update_dictionary
        instance = mock_celery_task_accessor_class.return_value
        instance.process_file.return_value = True
        mock_has_values_function.return_value = True

        return_value = self.app.put('/api/v1/aliquot/' + molecular_id,
                                    data=json.dumps(update_dictionary),
                                    content_type='application/json')
        print "-----------------" + str(return_value.status_code)
        print return_value.data
        assert return_value.status_code == 404
        assert exception_message in return_value.data


#if __name__ == '__main__':
    #unittest.main()
