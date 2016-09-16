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
        ('sample_controls',
         'IR_WAO85', [{"ion_reporter_id": "IR_WAO85", "molecular_id": "SC_SA1CB", "site": "mocha", "control_type": "no_template", "date_molecular_id_created": "2016-08-18 19:56:19.766"}, {"ion_reporter_id": "IR_WAO85", "molecular_id": "SC_SAWCB", "site": "mocha", "control_type": "no_template", "date_molecular_id_created": "2016-08-18 19:56:19.766"}, {"ion_reporter_id": "IR_WAO85", "molecular_id": "SC_67VKV", "site": "mocha", "control_type": "positive", "date_molecular_id_created": "2016-08-18 20:09:45.667"}], 200),

    )
    @unpack
    def test_get_file_url(self, sequence_data, ion_reporter_id, expected_return, returned_stat_code, mock_sc_accessor):
        sc_instance = mock_sc_accessor.return_value
        sc_instance.scan.return_value = expected_return


        return_value = self.app.get('/api/v1/ion_reporters/' + ion_reporter_id + '/' + sequence_data)
        print "==============" + str(return_value.status_code)
        assert return_value.status_code == returned_stat_code
        print "-----------------" +return_value.data
        print str(expected_return)
        print type(return_value.data)
        #assert str(expected_return) == return_value.data
