import unittest
from mock import patch
from ddt import ddt, data, unpack
import app
from tasks import tasks



@ddt
class TestTasks(unittest.TestCase):

    def setUp(self):

        self.app = app.app.test_client()
        pass

    @data(
        ({'site_ip_address': '129.43.127.133',
          'molecular_id_type': 'sample_control',
          'site': 'mocha',
          "ion_reporter_id": "IR_WAO85",
          'vcf_name': 'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.vcf',
          'molecular_id': 'SC_SA1CB',
          'analysis_id': 'SC_SA1CB_SC_SA1CB_a888_v1'
          },
         'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.tsv',
         {'analysis_id': 'SC_SA1CB_SC_SA1CB_a888_v1',
          'site': 'mocha',
          'molecular_id_type': 'sample_control',
          "ion_reporter_id": "IR_WAO85",
          'tsv_name': 'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.tsv',
          'vcf_name': 'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.vcf',
          'molecular_id': 'SC_SA1CB', 'site_ip_address': '129.43.127.133'}
         ),
        ({'site_ip_address': '129.43.127.133',
          'control_type': 'no_template',
          'molecular_id_type': 'sample_control',
          'site': 'mocha',
          "ion_reporter_id": "IR_WAO85",
          'dna_bam_name': 'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.bam',
          'molecular_id': 'SC_SA1CB',
          'analysis_id': 'SC_SA1CB_SC_SA1CB_a888_v1'
          },
         'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.bai',
         {'analysis_id': 'SC_SA1CB_SC_SA1CB_a888_v1', 'control_type': 'no_template',
          'dna_bam_name': 'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.bam',
          'site': 'mocha',
          'molecular_id_type': 'sample_control',
          "ion_reporter_id": "IR_WAO85",
          'dna_bai_name': 'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.bai',
          'molecular_id': 'SC_SA1CB', 'site_ip_address': '129.43.127.133'}
         ),
        ({'site_ip_address': '129.43.127.133',
          'control_type': 'no_template',
          'molecular_id_type': 'sample_control',
          'site': 'mocha',
          "ion_reporter_id": "IR_WAO85",
          'cdna_bam_name': 'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.bam',
          'molecular_id': 'SC_SA1CB',
          'analysis_id': 'SC_SA1CB_SC_SA1CB_a888_v1'
          },
         'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.bai',
         {'analysis_id': 'SC_SA1CB_SC_SA1CB_a888_v1', 'control_type': 'no_template', 'site': 'mocha',
          'molecular_id_type': 'sample_control',
          "ion_reporter_id": "IR_WAO85",
          'cdna_bam_name': 'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.bam',
          'cdna_bai_name': 'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.bai',
          'molecular_id': 'SC_SA1CB', 'site_ip_address': '129.43.127.133'}
         ),
        ({'site_ip_address': '129.43.127.133',
          'control_type': 'no_template',
          'molecular_id_type': 'sample_control',
          'site': 'mocha',
          "ion_reporter_id": "IR_WAO85",
          'qc_name': 'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.pdf',
          'molecular_id': 'SC_SA1CB',
          'analysis_id': 'SC_SA1CB_SC_SA1CB_a888_v1'
          },
         '',
         {'site_ip_address': '129.43.127.133',
          'control_type': 'no_template',
          'site': 'mocha',
          'molecular_id_type': 'sample_control',
          "ion_reporter_id": "IR_WAO85",
          'qc_name': 'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.pdf',
          'molecular_id': 'SC_SA1CB',
          'analysis_id': 'SC_SA1CB_SC_SA1CB_a888_v1'
          }
         )
    )
    @unpack
    @patch('common.auth0_authenticate.Auth0Authenticate.get_id_token')
    @patch('tasks.tasks.process_rule_by_tsv')
    @patch('tasks.tasks.post_tsv_info')
    @patch('tasks.tasks.S3Accessor')
    @patch('tasks.tasks.SequenceFileProcessor')
    def test_process_file_message(self, file_process_message, new_file_path, expected_return,
                                  mock_sf_accessor_class, mock_s3_accessor_class,
                                  mock_post_tsv_function, mock_process_rule_function, mock_token):

        s3_instance = mock_s3_accessor_class.return_value
        s3_instance.download.return_value = True
        s3_instance.upload.return_value = True
        sf_instance = mock_sf_accessor_class.return_value
        sf_instance.vcf_to_tsv.return_value = new_file_path
        sf_instance.bam_to_bai.return_value = new_file_path
        mock_post_tsv_function.return_value = True
        mock_process_rule_function.return_value = expected_return

        instance = mock_token.return_value
        instance.return_value = True

        return_value = tasks.process_file_message(file_process_message, id_token='auth_token')
        print "===================" + str(return_value)
        assert (return_value == expected_return)

    @data(
        ({'site_ip_address': '129.43.127.133',
          'control_type': 'no_template',
          'molecular_id_type': 'sample_control',
          'site': 'mocha',
          "ion_reporter_id": "IR_WAO85",
          'vcf_name': 'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.vcf',
          'molecular_id': 'SC_SA1CB',
          'analysis_id': 'SC_SA1CB_SC_SA1CB_a888_v1'
          },
         "Testing in process_file_message s3 download failed"
         ),
        ({'site_ip_address': '129.43.127.133',
          'control_type': 'no_template',
          'molecular_id_type': 'sample_control',
          'site': 'mocha',
          "ion_reporter_id": "IR_WAO85",
          'dna_bam_name': 'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.bam',
          'molecular_id': 'SC_SA1CB',
          'analysis_id': 'SC_SA1CB_SC_SA1CB_a888_v1'
          },
         "Testing in process_file_message s3 download failed"
         )
    )
    @unpack
    @patch('common.auth0_authenticate.Auth0Authenticate.get_id_token')
    @patch('tasks.tasks.S3Accessor')
    @patch('tasks.tasks.SequenceFileProcessor')
    def test_process_file_message_no_process_exception(self, file_process_message, exception_message,
                                                       mock_sf_accessor_class,
                                                       mock_s3_accessor_class, mock_token):
        s3_instance = mock_s3_accessor_class.return_value
        s3_instance.download.side_effect = Exception(exception_message)
        s3_instance.upload.return_value = True
        sf_instance = mock_sf_accessor_class.return_value
        sf_instance.vcf_to_tsv.return_value = True
        sf_instance.bam_to_bai.return_value = True

        instance = mock_token.return_value
        instance.return_value = True

        try:
            tasks.process_file_message(file_process_message, id_token='auth_token')
        except Exception as e:
            print "==================" + e.message
            assert exception_message in e.message

    @data(
        ({'site_ip_address': '129.43.127.133',
          'control_type': 'no_template',
          'molecular_id_type': 'sample_control',
          'site': 'mocha',
          "ion_reporter_id": "IR_WAO85",
          'vcf_name': 'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.vcf',
          'molecular_id': 'SC_SA1CB',
          'analysis_id': 'SC_SA1CB_SC_SA1CB_a888_v1'
          },
         "Testing in process_file_message vcf_to_tsv failed"
         )
    )
    @unpack
    @patch('common.auth0_authenticate.Auth0Authenticate.get_id_token')
    @patch('tasks.tasks.S3Accessor')
    @patch('tasks.tasks.SequenceFileProcessor')
    def test_process_file_message_vcf2tsv_exception(self, file_process_message, exception_message,
                                                    mock_sf_accessor_class,
                                                    mock_s3_accessor_class, mock_token):
        instance = mock_token.return_value
        instance.return_value = True

        s3_instance = mock_s3_accessor_class.return_value
        s3_instance.download.return_value = True
        s3_instance.upload.return_value = True
        sf_instance = mock_sf_accessor_class.return_value
        sf_instance.vcf_to_tsv.side_effect = Exception(exception_message)
        sf_instance.bam_to_bai.return_value = True

        try:
            tasks.process_file_message(file_process_message, id_token='auth_token')
        except Exception as e:
            print "==================" + e.message
            assert exception_message in e.message

    @data(
        ({'site_ip_address': '129.43.127.133',
          'control_type': 'no_template',
          'molecular_id_type': 'sample_control',
          'site': 'mocha',
          "ion_reporter_id": "IR_WAO85",
          'dna_bam_name': 'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.bam',
          'molecular_id': 'SC_SA1CB',
          'analysis_id': 'SC_SA1CB_SC_SA1CB_a888_v1'
          },
         "Testing in process_file_message bam_to_bai failed"
         )
    )
    @unpack
    @patch('common.auth0_authenticate.Auth0Authenticate.get_id_token')
    @patch('tasks.tasks.S3Accessor')
    @patch('tasks.tasks.SequenceFileProcessor')
    def test_process_file_message_bam2bai_exception(self, file_process_message, exception_message,
                                                    mock_sf_accessor_class,
                                                    mock_s3_accessor_class, mock_token):
        instance = mock_token.return_value
        instance.return_value = True

        s3_instance = mock_s3_accessor_class.return_value
        s3_instance.download.return_value = True
        s3_instance.upload.return_value = True
        sf_instance = mock_sf_accessor_class.return_value
        sf_instance.vcf_to_tsv.return_value = True
        sf_instance.bam_to_bai.side_effect = Exception(exception_message)

        try:
            tasks.process_file_message(file_process_message, id_token='auth_token')
        except Exception as e:
            print "==================" + e.message
            assert exception_message in e.message



# if __name__ == '__main__':
#     unittest.main()