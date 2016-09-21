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
              "ion_reporter_id": "IR_WAO85",
              'vcf_name': 'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.vcf',
              'molecular_id': 'SC_SA1CB',
              'analysis_id': 'SC_SA1CB_SC_SA1CB_a888_v1'
              },
             'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.tsv',
             {'analysis_id': 'SC_SA1CB_SC_SA1CB_a888_v1', 'control_type': 'no_template', 'site': 'mocha',
              "ion_reporter_id": "IR_WAO85",
              'tsv_name': 'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.tsv',
              'vcf_name': 'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.vcf',
              'molecular_id': 'SC_SA1CB', 'site_ip_address': '129.43.127.133'}
            ),
            ({'site_ip_address': '129.43.127.133',
              'control_type': 'no_template',
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
              "ion_reporter_id": "IR_WAO85",
              'dna_bai_name': 'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.bai',
              'molecular_id': 'SC_SA1CB', 'site_ip_address': '129.43.127.133'}
            ),
            ({'site_ip_address': '129.43.127.133',
              'control_type': 'no_template',
              'site': 'mocha',
              "ion_reporter_id": "IR_WAO85",
              'cdna_bam_name': 'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.bam',
              'molecular_id': 'SC_SA1CB',
              'analysis_id': 'SC_SA1CB_SC_SA1CB_a888_v1'
              },
             'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.bai',
             {'analysis_id': 'SC_SA1CB_SC_SA1CB_a888_v1', 'control_type': 'no_template', 'site': 'mocha',
              "ion_reporter_id": "IR_WAO85",
              'cdna_bam_name': 'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.bam',
              'cdna_bai_name': 'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.bai',
              'molecular_id': 'SC_SA1CB', 'site_ip_address': '129.43.127.133'}
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

    #TODO add test exception, and test else ...

# if __name__ == '__main__':
#     unittest.main()