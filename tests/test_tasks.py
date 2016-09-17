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
              'control_type': 'no_template',
              'site': 'mocha',
              'vcf_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_v2.vcf',
              'molecular_id': 'SC_YQ111',
              'analysis_id': 'SC_YQ111_SC_YQ111_k123_v1'
              },
             'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_v2.tsv',
             {'analysis_id': 'SC_YQ111_SC_YQ111_k123_v1', 'control_type': 'no_template', 'site': 'mocha',
              'tsv_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_v2.tsv',
              'vcf_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_v2.vcf',
              'molecular_id': 'SC_YQ111', 'site_ip_address': '129.43.127.133'}
            ),
            ({'site_ip_address': '129.43.127.133',
              'control_type': 'no_template',
              'site': 'mocha',
              'dna_bam_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_DNA_v2.bam',
              'molecular_id': 'SC_YQ111',
              'analysis_id': 'SC_YQ111_SC_YQ111_k123_v1'
              },
             'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_DNA_v2.bai',
             {'analysis_id': 'SC_YQ111_SC_YQ111_k123_v1', 'control_type': 'no_template',
              'dna_bam_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_DNA_v2.bam',
              'site': 'mocha',
              'dna_bai_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_DNA_v2.bai',
              'molecular_id': 'SC_YQ111', 'site_ip_address': '129.43.127.133'}
            ),
            ({'site_ip_address': '129.43.127.133',
              'control_type': 'no_template',
              'site': 'mocha',
              'cdna_bam_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam',
              'molecular_id': 'SC_YQ111',
              'analysis_id': 'SC_YQ111_SC_YQ111_k123_v1'
              },
             'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bai',
             {'analysis_id': 'SC_YQ111_SC_YQ111_k123_v1', 'control_type': 'no_template', 'site': 'mocha',
              'cdna_bam_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam',
              'cdna_bai_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bai',
              'molecular_id': 'SC_YQ111', 'site_ip_address': '129.43.127.133'}
            )
         )
    @unpack
    @patch('tasks.tasks.S3Accessor')
    @patch('tasks.tasks.SequenceFileProcessor')
    def test_process_file_message(self, file_process_message, new_file_path, expected_return, mock_sf_accessor_class, mock_s3_accessor_class):

        s3_instance = mock_s3_accessor_class.return_value
        s3_instance.download.return_value = True
        s3_instance.upload.return_value = True
        sf_instance = mock_sf_accessor_class.return_value
        sf_instance.vcf_to_tsv.return_value = new_file_path
        sf_instance.bam_to_bai.return_value = new_file_path

        return_value = tasks.process_file_message(file_process_message)
        print "===================" + str(return_value)
        assert (return_value == expected_return)


# if __name__ == '__main__':
#     unittest.main()