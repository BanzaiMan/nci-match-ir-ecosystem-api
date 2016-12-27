from unittest import TestCase
from mock import patch
patch('resources.auth0_resource.requires_auth', lambda x: x).start()
from resources.s3_authentication_policy import s3_resource
from ddt import ddt, data, unpack
import app

@ddt
class TestS3AuthenticationPolicy(TestCase):

    def setUp(self):
        self.app = app.app.test_client()
        pass
#TODO: add passing 200
    @data(
        ('IR_WAO85','SC_SA1CB', 'SC_SA1CB_SC_SA1CB_a888_v1', 'SC_SA1CB_SC_SA1CB_analysis888_v1_QC.pdf', ('fields', 'policy', 'AWSAccessKeyId', 'signature'), 409),
        ('', 'SC_SA1CB', 'SC_SA1CB_SC_SA1CB_a888_v1', 'SC_SA1CB_SC_SA1CB_analysis888_v1_QC.pdf', ('fields', 'policy', 'AWSAccessKeyId', 'signature'), 404),
        ('', '', 'SC_SA1CB_SC_SA1CB_a888_v1', 'SC_SA1CB_SC_SA1CB_analysis888_v1_QC.pdf',
         ('fields', 'policy', '', 'signature'), 404),
        ('', 'SC_SA1CB', 'SC_SA1CB_SC_SA1CB_a888_v1', 'SC_SA1CB_SC_SA1CB_analysis888_v1_QC.pdf',
         ('fields', 'policy', '', 'signature'), 404),
        ('', 'SC_SA1CB', 'SC_SA1CB_SC_SA1CB_a888_v1', 'SC_SA1CB_SC_SA1CB_analysis888_v1_QC.pdf',
         ('fields', 'policy', 'AWSAccessKeyId', ''), 404)

    )
    @unpack
    # @patch('resources.s3_authentication_policy.s3_resource')
    @patch('resources.s3_authentication_policy.bucket2')
    def test_get(self, ion_reporter_id, molecular_id, analysis_id, file_name, list, status_code, mock_resource):
    # def test_get(self, ion_reporter_id, molecular_id, analysis_id, file_name, list, status_code):
        # s3_instance = mock_s3_resource.return_value
        # s3_instance.ObjectSummary.return_value = True

        s3_instance = mock_resource.objects.filter
        s3_instance.return_value = [s3_resource.ObjectSummary(bucket_name='pedmatch-dev', key=u'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1_QC.pdf')]

        return_value = self.app.get('/api/v1/sample_controls/files/' + ion_reporter_id + '/' + molecular_id+ '/' + analysis_id+ '/' + file_name)

        # print return_value
        print return_value.status_code
        # print return_value.data
        if 'policy' in return_value.data:
            for i in list:
                assert i in return_value.data
        else:
            assert return_value.status_code == status_code

    # # TODO: add 500
    @data(
        ('IR_WAO85','SC_SA1CB', 'SC_SA1CB_SC_SA1CB_a888_v1', 'SC_SA1CB_SC_SA1CB_analysis888_v1_QC.pdf', ('fields', 'policy', 'AWSAccessKeyId', 'signature'), 409),
        ('', 'SC_SA1CB', 'SC_SA1CB_SC_SA1CB_a888_v1', 'SC_SA1CB_SC_SA1CB_analysis888_v1_QC.pdf', ('fields', 'policy', 'AWSAccessKeyId', 'signature'), 404),
        ('', '', 'SC_SA1CB_SC_SA1CB_a888_v1', 'SC_SA1CB_SC_SA1CB_analysis888_v1_QC.pdf',
         ('fields', 'policy', '', 'signature'), 404),
        ('', 'SC_SA1CB', 'SC_SA1CB_SC_SA1CB_a888_v1', 'SC_SA1CB_SC_SA1CB_analysis888_v1_QC.pdf',
         ('fields', 'policy', '', 'signature'), 404),
        ('', 'SC_SA1CB', 'SC_SA1CB_SC_SA1CB_a888_v1', 'SC_SA1CB_SC_SA1CB_analysis888_v1_QC.pdf',
         ('fields', 'policy', 'AWSAccessKeyId', ''), 404)

    )
    @unpack
    @patch('resources.s3_authentication_policy.bucket2')
    @patch('resources.s3_authentication_policy.s3Client')
    def test_get_exception(self, ion_reporter_id, molecular_id, analysis_id, file_name, list, status_code, s3_mock, mock_resource):
        s3_instance2 = mock_resource.objects.filter
        s3_instance2.return_value = [s3_resource.ObjectSummary(bucket_name='pedmatch-dev',
                                                              key=u'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1_QC.pdf')]

        s3_instance = s3_mock.return_value
        s3_instance.generate_presigned_post.return_value = False

        return_value = self.app.get('/api/v1/sample_controls/files/' + ion_reporter_id + '/' + molecular_id+ '/' + analysis_id+ '/' + file_name)

        # print return_value
        print return_value.status_code
        # print return_value.data
        if 'policy' in return_value.data:
            for i in list:
                assert i in return_value.data
        else:
            assert return_value.status_code == status_code
