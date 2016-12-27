from unittest import TestCase
from mock import patch
patch('resources.auth0_resource.requires_auth', lambda x: x).start()
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
    def test_get(self, ion_reporter_id, molecular_id, analysis_id, file_name, list, status_code):

        return_value = self.app.get('/api/v1/sample_controls/files/' + ion_reporter_id + '/' + molecular_id+ '/' + analysis_id+ '/' + file_name)

        # print return_value
        # print return_value.status_code
        # print return_value.data
        if 'policy' in return_value.data:
            for i in list:
                assert i in return_value.data
        else:
            assert return_value.status_code == status_code

    # TODO: add 500
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
    @patch('resources.s3_authentication_policy.s3Client')
    def test_get_exception(self, ion_reporter_id, molecular_id, analysis_id, file_name, list, status_code, s3_mock):
        s3_instance = s3_mock.return_value
        s3_instance.generate_presigned_post.return_value = False

        return_value = self.app.get('/api/v1/sample_controls/files/' + ion_reporter_id + '/' + molecular_id+ '/' + analysis_id+ '/' + file_name)

        # print return_value
        # print return_value.status_code
        # print return_value.data
        if 'policy' in return_value.data:
            for i in list:
                assert i in return_value.data
        else:
            assert return_value.status_code == status_code
