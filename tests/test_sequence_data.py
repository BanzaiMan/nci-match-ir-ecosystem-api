import unittest
from mock import patch
from ddt import ddt, data, unpack
import app
import json


@ddt
@patch('resources.sequence_data.SampleControlAccessor')
class TestSequenceData(unittest.TestCase):

    def setUp(self):
        self.app = app.app.test_client()
        pass

    @data(
        # Should be returning a 404
        ('sample_controls',
         'IR_WAO95', "No sample controls sequenced with id:", 200, {'projection': None}),

        ('patients',
         'IR_WAO85', {u'message': u'Finding patients sequenced with IR: IR_WAO85 not yet implemented.'}, 501, {'projection': ['site_ip_address', 'control_type', 'molecular_id']}),

       # Should be returning a 400.
        ('waleeds',
         'IR_WAO85', {u'message': u'Can only request patients or sample_controls. You requested: waleeds. '
                                  u'You have requested this URI [/api/v1/ion_reporters/IR_WAO85/waleeds] but did you '
                                  u'mean /api/v1/ion_reporters/<string:ion_reporter_id> or '
                                  u'/api/v1/ion_reporters/version or /api/v1/ion_reporters ?'}, 404, {'projection': ['site_ip_address', 'control_type', 'molecular_id']}),
        ('sample_controls',
         'IR_WAO85', [
             {"ion_reporter_id": "IR_WAO85", "molecular_id": "SC_SA1CB", "site": "mocha", "control_type": "no_template",
              "date_molecular_id_created": "2016-08-18 19:56:19.766"},
             {"ion_reporter_id": "IR_WAO85", "molecular_id": "SC_SAWCB", "site": "mocha", "control_type": "no_template",
              "date_molecular_id_created": "2016-08-18 19:56:19.766"},
             {"ion_reporter_id": "IR_WAO85", "molecular_id": "SC_67VKV", "site": "mocha", "control_type": "positive",
              "date_molecular_id_created": "2016-08-18 20:09:45.667"}], 200, {'projection': None}),
        ('sample_controls',
         'IR_WAO85', [{u'control_type': u'no_template', u'molecular_id': u'SC_SA1CB'}, {u'control_type': u'no_template', u'molecular_id': u'SC_SAWCB'}, {u'control_type': u'positive', u'molecular_id': u'SC_67VKV'}], 200,
         {'projection': ['site_ip_address', 'control_type', 'molecular_id']}),
    )
    @unpack
    @patch('resources.sequence_data.reqparse.RequestParser.parse_args')
    def test_get(self, sequence_data, ion_reporter_id, expected_return, returned_stat_code, args, mock_parse_args_function, mock_sc_accessor):
        mock_parse_args_function.return_value = args
        sc_instance = mock_sc_accessor.return_value
        sc_instance.scan.return_value = expected_return
        return_value = self.app.get('/api/v1/ion_reporters/' + ion_reporter_id + '/' + sequence_data)
        print return_value.status_code
        print json.loads(return_value.data)
        assert return_value.status_code == returned_stat_code
        assert expected_return == json.loads(return_value.data)

    @data(
        ('sample_controls',
         'IR_WAO85', 'Server Error contact help', 500),

    )
    @unpack
    def test_get_exception(self, sequence_data, ion_reporter_id, expected_return, returned_stat_code, mock_sc_accessor):
        sc_instance = mock_sc_accessor.return_value
        sc_instance.scan.side_effect = Exception(expected_return)
        return_value = self.app.get('/api/v1/ion_reporters/' + ion_reporter_id + '/' + sequence_data)
        print return_value.status_code
        print return_value.data
        assert return_value.status_code == returned_stat_code
        assert expected_return in return_value.data
