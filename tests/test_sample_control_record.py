import unittest
import json
from ddt import ddt, data, unpack
from mock import patch
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
             "site": "mocha"}, 'SC_YQ111', 200),
        ({}, 'SC_YQ999', 404)
    )
    @unpack
    @patch('resources.sample_control_record.SampleControlAccessor')
    def test_get(self, item, molecular_id, expected_results, mock_sc_record_class):
        instance = mock_sc_record_class.return_value
        instance.get_item.return_value = item
        return_value = self.app.get('/api/v1/sample_controls/' + molecular_id)

        assert return_value.status_code == expected_results
        print return_value.data
        if expected_results == 200:
            assert len(return_value.data) > 0
            assert (json.loads(return_value.data))['site'] == "mocha"
        else:
            print return_value.data
            assert return_value.data.find("message")

    @patch('resources.sample_control_record.SampleControlAccessor')
    def test_get_exception(self, mock_sc_record_class):
        instance = mock_sc_record_class.return_value
        instance.get_item.side_effect = Exception('Testing get_item exception')
        return_value = self.app.get('/api/v1/sample_controls/SC_5AMCC')
        assert return_value.status_code == 500
        assert "Testing get_item exception" in return_value.data

    @data(
        ('SC_5AMCC', '"message": "Item deleted"')
    )
    @unpack
    @patch('resources.record.Record.record_exist')
    @patch('resources.sample_control_record.CeleryTaskAccessor')
    def test_delete(self, molecular_id, expected_results, mock_sc_record_class, mock_method):
        mock_method.return_value = True
        instance = mock_sc_record_class.return_value
        instance.delete_item.return_value = True
        return_value = self.app.delete('/api/v1/sample_controls/' + molecular_id)

        assert return_value.data.find(expected_results)

    @data(
        ('SC_5AMCC', 'Celery Task Accessor blew up!', True, 500),
        ('SC_5AMCC', 'No ABCMeta with id', False, 404)
    )
    @unpack
    @patch('resources.record.Record.record_exist')
    @patch('resources.sample_control_record.CeleryTaskAccessor')
    def test_delete_exception(self, molecular_id, expected_message, record_exist_return, status_code, mock_celery_class,
                              mock_record_exist_method):
        mock_record_exist_method.return_value = record_exist_return
        instance = mock_celery_class.return_value
        instance.delete_sample_control_record.side_effect = Exception(expected_message)
        return_value = self.app.delete('/api/v1/sample_controls/' + molecular_id)
        assert return_value.status_code == status_code
        assert expected_message in return_value.data

    @data(
        ('SC_5AMCC',
         {'vcf_name': 'mocha/SC_5AMCC/SC_5AMCC_SC_5AMCC_k123_v1/SC_5AMCC_SC_5AMCC_analysis667_v1.vcf', 'site': 'mocha',
          'molecular_id': 'SC_5AMCC', 'analysis_id': 'SC_5AMCC_SC_5AMCC_k123_v1'}, 'updated', True)
    )
    @unpack
    @patch('resources.record.Record.record_exist')
    @patch('resources.sample_control_record.CeleryTaskAccessor')
    def test_put(self, molecular_id, update_dictionary, expected_results, record_exist_return, mock_celery_class,
                 mock_record_exist_method):
        mock_record_exist_method.return_value = record_exist_return
        instance = mock_celery_class.return_value
        instance.update_sample_control_record(update_dictionary).return_value = True
        return_value = self.app.put('/api/v1/sample_controls/' + molecular_id,
                                    data=json.dumps(update_dictionary),
                                    content_type='application/json')
        print return_value.data
        print (molecular_id + " " + expected_results)
        assert (molecular_id + " " + expected_results) in return_value.data

    @data(
        ('SC_5AMCC',
         {'vcf_name': 'mocha/SC_5AMCC/SC_5AMCC_SC_5AMCC_k123_v1/SC_5AMCC_SC_5AMCC_analysis667_v1.vcf', 'site': 'mocha',
          'molecular_id': 'SC_5AMCC', 'analysis_id': 'SC_5AMCC_SC_5AMCC_k123_v1'}, True, 500,
         'Testing update_item exception'),
        ('SC_5AMCC',
         {'vcf_name': 'mocha/SC_5AMCC/SC_5AMCC_SC_5AMCC_k123_v1/SC_5AMCC_SC_5AMCC_analysis667_v1.vcf', 'site': 'mocha',
          'molecular_id': 'SC_5AMCC', 'analysis_id': 'SC_5AMCC_SC_5AMCC_k123_v1'}, False, 404, 'No ABCMeta with id:')
    )
    @unpack
    @patch('resources.record.Record.record_exist')
    @patch('resources.sample_control_record.CeleryTaskAccessor')
    def test_put_exception(self, molecular_id, update_dictionary, record_exist_return, status_code, expected_message,
                           mock_celery_class, mock_record_exist_method):
        mock_record_exist_method.return_value = record_exist_return
        instance = mock_celery_class.return_value
        instance.update_sample_control_record.side_effect = Exception(expected_message)
        return_value = self.app.put('/api/v1/sample_controls/' + molecular_id,
                                    data=json.dumps(update_dictionary),
                                    content_type='application/json')
        print return_value.data
        assert return_value.status_code == status_code
        assert expected_message in return_value.data

# if __name__ == '__main__':
#     unittest.main()
