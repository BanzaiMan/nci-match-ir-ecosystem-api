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
        ('IR_WAO85', 'patients', {'projection': ['site_ip_address', 'control_type', 'molecular_id']},
         '<Response streamed [501 NOT IMPLEMENTED]>'),
            ('IR_WAO85', 'sample_controls', {'projection': ['site_ip_address', 'control_type', 'molecular_id']},
             '<Response streamed [404 NOT FOUND]>')
    )
    @unpack
    def test_get_file_url(self, ion_reporter_id, sequence_data, args, expected_return, mock_sc_accessor):
        s3_instance = mock_sc_accessor.return_value
        s3_instance().scan.return_value = expected_return

        try:
            return_value = self.app.get('/api/v1/ion_reporters/' + ion_reporter_id + '/' + sequence_data)
            print return_value
            assert expected_return == str(return_value)
        except Exception as e:
            print e
            assert expected_return == str(e)