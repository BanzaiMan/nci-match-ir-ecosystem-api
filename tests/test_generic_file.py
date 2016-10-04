from unittest import TestCase
from mock import patch
from ddt import ddt, data, unpack
import app
import json

@ddt
@patch('resources.sequence_data.SampleControlAccessor')
class TestGenericFile(TestCase):

    def setUp(self):
        self.app = app.app.test_client()
        pass

    @data(
        ('SC_SA1CB', 'qc', "u's3_download_file_url': u'https://pedmatch-dev.s3.amazonaws.com/IR_WAO85/"
                           "SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1_QC.pdf?", 200),
        ('SC_SA1C', 'qc', "u'SC_SA1C was not found.", 404)
    )
    @unpack
    def test_get_file_url(self, molecular_id, file_type, return_message, returned_stat_code, mock_sc_accessor):
        sc_instance = mock_sc_accessor.return_value
        sc_instance.get_item.return_value = True
        return_value = self.app.get('/api/v1/files/' + molecular_id + '/' + file_type)
        print return_value.status_code
        print return_message
        print str(json.loads(return_value.data))
        assert return_value.status_code == returned_stat_code
        assert return_message in str(json.loads(return_value.data))

