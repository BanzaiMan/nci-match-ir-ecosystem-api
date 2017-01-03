import unittest
from ddt import ddt, data, unpack
from mock import patch
from common.datetime_helper import DateTimeHelper

import app
import json


@ddt
class TestApp(unittest.TestCase):

    def setUp(self):
        self.app=app.app.test_client()
        pass

    @data((1, 'TravisBuild'))
    @unpack
    def test_version(self, inp, expected_return_data):
        return_value = self.app.get('/api/v1/ion_reporters/version')
        print json.loads(return_value.data)
        # assert json.loads(return_value.data) == json.loads(expected_return_data)
        assert expected_return_data in return_value.data


    #@patch('common.datetime_helper.datetime.datetime.strftime')
    #@patch('datetime.datetime.utcnow')
    #@data({'str-format': '%Y-%m-%d %H:%M:%S.%f'})
    #@unpack
    @patch('__builtin__.str')
    @patch('string.split')
    def test_utc_millisecond_timestamp(self, m_split, m_str):
        DateTimeHelper.get_utc_millisecond_timestamp()
        # s3upload = s3_upload.S3Upload('bucket', 'clia_location', 'msn', 'analysis_id', 'Tissue', input_list, True)
        # s3upload.populate_upload_set(input_list)
        # assert s3upload.upload_file_set == set()
        #assert m_strftime.called_once_with(str_format)
        assert m_split.called_once_with('.')
        assert m_str.called_once()


# if __name__ == '__main__':
#     unittest.main()






