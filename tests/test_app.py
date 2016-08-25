import unittest

from ddt import ddt, data, unpack
from mock import patch

import sys
sys.path.append('..')
from common.datetime_helper import DateTimeHelper

#from datetime import datetime

@ddt
class TestApp(unittest.TestCase):

    def setUp(self):
        pass

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

# TODO: write unittests. Start with something simple like the dictionaryHelper, QueryHelper, and StringHelper
if __name__ == '__main__':
    unittest.main()






