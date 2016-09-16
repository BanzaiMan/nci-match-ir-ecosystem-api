import unittest
import app
from ddt import ddt, data, unpack
from mock import patch
from accessors.s3_accessor import S3Accessor

@ddt
class TestS3Accessor(unittest.TestCase):

    def setUp(self):
        self.app = app.app.test_client()


    @data(
        ('/tmp/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam',
         'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam')
    )
    @unpack
    @patch('accessors.s3_accessor.boto3')
    def test_upload(self, local_file_path, file_s3_path, mock_boto3):
        instance = mock_boto3.return_value
        instance.client.return_value = True
        instance.resource.return_value = True
        s3_accessor = S3Accessor()
        s3_accessor.resource.meta.client.upload_file.return_value = True
        return_value = s3_accessor.upload(local_file_path, file_s3_path)
        print "===============" + str(return_value)
        assert (return_value == None)


    @data(
        ('/tmp/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam',
         'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam',
         'Testing s3 upload exception')
    )
    @unpack
    @patch('accessors.s3_accessor.boto3')
    def test_upload_exception(self, local_file_path, file_s3_path, exception_message, mock_boto3):
        instance = mock_boto3.return_value
        instance.client.return_value = True
        instance.resource.return_value = True
        s3_accessor = S3Accessor()
        s3_accessor.resource.meta.client.upload_file.side_effect = Exception(exception_message)
        try:
            s3_accessor.upload(local_file_path, file_s3_path)
        except Exception as e:
            assert (e.message == exception_message)


    @data(
        ('mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam',
         '/tmp/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam')
    )
    @unpack
    @patch('accessors.s3_accessor.boto3')
    def test_download(self, file_s3_path, expected_return, mock_boto3):
        instance = mock_boto3.return_value
        instance.client.return_value = True
        instance.resource.return_value = True
        s3_accessor = S3Accessor()
        s3_accessor.resource.meta.client.download_file.return_value = True
        return_value = s3_accessor.download(file_s3_path)
        print "===============" + str(return_value)
        assert (return_value == expected_return)


    @data(
        ('/tmp/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam',
         'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam',
         'Testing s3 download exception')
    )
    @unpack
    @patch('accessors.s3_accessor.boto3')
    def test_download_exception(self, local_file_path, file_s3_path, exception_message, mock_boto3):
        instance = mock_boto3.return_value
        instance.client.return_value = True
        instance.resource.return_value = True
        s3_accessor = S3Accessor()
        s3_accessor.resource.meta.client.download_file.side_effect = Exception(exception_message)
        try:
            s3_accessor.download(file_s3_path)
        except Exception as e:
            assert (e.message == exception_message)


    @data(
            ('mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam',
             'https://pedmatch-dev.s3.amazonaws.com/mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam?AWSAccessKeyId=AKIAIJLVHIQJ3UBNO6OA&Expires=1473369011&Signature=u9fDnHtEH%2Bf70O1fV1kBBNEDXWQ%3D',
             'https://pedmatch-dev.s3.amazonaws.com/mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam?AWSAccessKeyId=AKIAIJLVHIQJ3UBNO6OA&Expires=1473369011&Signature=u9fDnHtEH%2Bf70O1fV1kBBNEDXWQ%3D'
             )
    )
    @unpack
    @patch('accessors.s3_accessor.boto3')
    def test_get_download_url(self, file_s3_path, generate_presigned_url_return, expected_return, mock_boto3):
        instance = mock_boto3.return_value
        instance.client.return_value = True
        instance.resource.return_value = True
        s3_accessor = S3Accessor()
        s3_accessor.client.generate_presigned_url.return_value = generate_presigned_url_return
        return_value = s3_accessor.get_download_url(file_s3_path)
        print "==============================="
        print return_value
        assert(return_value==expected_return)


    @data(('mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam',
           'Testing get_download_url exception'))
    @unpack
    @patch('accessors.s3_accessor.boto3')
    def test_get_download_url_exception(self, file_s3_path, exception_message, mock_boto3):
        instance = mock_boto3.return_value
        instance.client.return_value = True
        instance.resource.return_value = True
        s3_accessor = S3Accessor()
        s3_accessor.client.generate_presigned_url.side_effect = Exception(exception_message)
        try:
            s3_accessor.get_download_url(file_s3_path)
        except Exception as e:
            assert (e.message == exception_message)

# if __name__ == '__main__':
#     unittest.main()