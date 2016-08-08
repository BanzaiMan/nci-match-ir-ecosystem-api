import unittest
import os.path
import sys
from mock import patch, MagicMock
from ddt import ddt, data, unpack

sys.path.append("..")
from dynamodb import aws
#from s3_transfer import aws


@ddt
class TestDynamodbService(unittest.TestCase):

    def setUp(self):
        pass

    @data(('test_aws_config','../resources/.aws_credentials.json'))
    @unpack
    @patch('__builtin__.open')
    @patch('os.path.isfile')
    @patch('json.load')
    @patch('os.path.dirname')
    @patch('os.path.join')
    def test_aws_credentials(self, test_what, file_name, m_join, m_dirname, m_load, m_isfile, m_fileopen):
        s3_conf = file_name
        curr_dir = os.path.dirname(__file__)
        file_nam = os.path.join(curr_dir, s3_conf)

        aws.aws_credentials()
        assert m_join.called
        assert m_dirname.called_once_with(__file__)
        assert m_isfile.called_once_with(file_nam)
        assert m_fileopen.called_once_with(file_nam)
        assert m_load.called


    @data(('test_aws_config', '../resources/.aws_credentials.json'))
    @unpack
    @patch('__builtin__.open')
    @patch('os.path.isfile')
    @patch('json.load')
    @patch('os.path.dirname')
    @patch('os.path.join')
    def test_aws_credentials2(self, test_what, file_name, m_join, m_dirname, m_load, m_isfile, m_fileopen):
        s3_conf = file_name
        curr_dir = os.path.dirname(__file__)
        file_nam = os.path.join(curr_dir, s3_conf)
        m_isfile.return_value = False

        aws.aws_credentials()
        assert m_join.called
        assert m_dirname.called_once_with(__file__)
        assert m_isfile.called_once_with(file_nam)
        assert not m_fileopen.called
        assert not m_load.called


    @data(('test_aws_config', '../resources/.aws_credentials.json', ''))
    @unpack
    @patch('__builtin__.print')
    @patch('__builtin__.open')
    @patch('os.path.isfile')
    @patch('json.load')
    @patch('os.path.dirname')
    @patch('os.path.join')
    def test_aws_credentials3(self, test_what, file_name, json_load, m_join, m_dirname, m_load, m_isfile, m_fileopen, m_print):
        s3_conf = file_name
        curr_dir = os.path.dirname(__file__)
        file_nam = os.path.join(curr_dir, s3_conf)
        m_load.return_value = json_load

        aws.aws_credentials()
        assert m_join.called
        assert m_dirname.called_once_with(__file__)
        assert m_isfile.called_once_with(file_nam)
        assert m_fileopen.called
        assert m_load.called
        assert m_print.called_once_with('aws credentials not found.')

    # #@data(('test_dynamodb_service', 'mmm', 'nnn'))
    # #@unpack
    # @patch('dynamodb.aws.aws_credentials')
    # def test_dynamodb_service(self, m_credentials):
    #     db_service = aws.DynamoDBService()
    #     #m_credentials.return_value = (credential1, credential2)
    #     assert m_credentials.called

if __name__ == '__main__':
    unittest.main()
