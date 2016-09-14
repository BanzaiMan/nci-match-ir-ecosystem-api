import unittest
from mock import patch
from ddt import ddt, data, unpack
import sys
sys.path.append("..")
import app
import json

@ddt
class TestSequenceFile(unittest.TestCase):

    def setUp(self):
        self.app = app.app.test_client()
        pass

    @data(
        ('SC_YQ111', 'vcf', None,
         {'site_ip_address': '129.43.127.133',
          'control_type': 'no_template',
          'dna_bam_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_DNA_v2.bam',
          'site': 'mocha',
          'qc_name': 'None',
          'dna_bai_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_DNA_v2.bai',
          'tsv_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_v2.tsv',
          'cdna_bam_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam',
          'vcf_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_v2.vcf',
          'cdna_bai_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bai',
          'date_molecular_id_created': '2016-08-28 16:56:29.333',
          'molecular_id': 'SC_YQ111',
          'analysis_id': 'SC_YQ111_SC_YQ111_k123_v1'
          },
         'https://pedmatch-dev.s3.amazonaws.com/mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_v2.vcf?AWSAccessKeyId=AKIAIJLVHIQJ3UBNO6OA&Expires=1473351631&Signature=9qPN9uVxObqACIr28zBe13%2F%2FtjU%3D',
         'https://pedmatch-dev.s3.amazonaws.com/mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_v2.vcf?AWSAccessKeyId=AKIAIJLVHIQJ3UBNO6OA&Expires=1473351631&Signature=9qPN9uVxObqACIr28zBe13%2F%2FtjU%3D'
         ),
        ('SC_YQ111', 'bam', 'cdna',
         {'site_ip_address': '129.43.127.133',
          'control_type': 'no_template',
          'dna_bam_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_DNA_v2.bam',
          'site': 'mocha',
          'qc_name': 'None',
          'dna_bai_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_DNA_v2.bai',
          'tsv_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_v2.tsv',
          'cdna_bam_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam',
          'vcf_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_v2.vcf',
          'cdna_bai_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bai',
          'date_molecular_id_created': '2016-08-28 16:56:29.333',
          'molecular_id': 'SC_YQ111',
          'analysis_id': 'SC_YQ111_SC_YQ111_k123_v1'
          },
         'https://pedmatch-dev.s3.amazonaws.com/mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam?AWSAccessKeyId=AKIAIJLVHIQJ3UBNO6OA&Expires=1473369011&Signature=u9fDnHtEH%2Bf70O1fV1kBBNEDXWQ%3D',
         'https://pedmatch-dev.s3.amazonaws.com/mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam?AWSAccessKeyId=AKIAIJLVHIQJ3UBNO6OA&Expires=1473369011&Signature=u9fDnHtEH%2Bf70O1fV1kBBNEDXWQ%3D'
         )
    )
    @unpack
    @patch('resources.sequence_file.SampleControlAccessor')
    @patch('resources.sequence_file.S3Accessor')
    def test_get_file_url(self, molecular_id, file_format, nucleic_acid_type, item, get_download_url_return,
                          expect_return, mock_s3_accessor, mock_sc_accessor):
        s3_instance = mock_s3_accessor.return_value
        s3_instance.get_download_url.return_value = get_download_url_return
        instance = mock_sc_accessor.return_value
        instance.get_item.return_value = item

        if nucleic_acid_type is None:
            return_value = self.app.get('/api/v1/sequence_files/' + molecular_id + '/' + file_format)
        else:
            return_value = self.app.get(
                '/api/v1/sequence_files/' + molecular_id + '/' + file_format + '/' + nucleic_acid_type)

        print return_value.data
        assert (json.loads(return_value.data)["s3_download_file_url"] == expect_return)

if __name__ == '__main__':
    unittest.main()
