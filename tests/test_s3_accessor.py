import unittest
import app
from ddt import ddt, data, unpack
from mock import patch
from accessors.s3_accessor import S3Accessor

@ddt
class TestSampleControlRecord(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()

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



if __name__ == '__main__':
    unittest.main()