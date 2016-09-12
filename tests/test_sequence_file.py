import unittest
from mock import patch
import sys
sys.path.append("..")
from resources.sequence_file import SequenceFile
from ddt import ddt, data, unpack
import app


@ddt
class TestSequenceFile(unittest.TestCase):

    def setUp(self):
        self.app = app.app.test_client()
        pass

    @data(
           ('SC_YQ111', 'vcf_name',
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
           ('SC_YQ111', 'tsv_name',
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
           'https://pedmatch-dev.s3.amazonaws.com/mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_v2.tsv?AWSAccessKeyId=AKIAIJLVHIQJ3UBNO6OA&Expires=1473368421&Signature=vHec6R49WY2kzRGOt%2FkveDxKE2A%3D',
            'https://pedmatch-dev.s3.amazonaws.com/mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_v2.tsv?AWSAccessKeyId=AKIAIJLVHIQJ3UBNO6OA&Expires=1473368421&Signature=vHec6R49WY2kzRGOt%2FkveDxKE2A%3D'
           ),
           ('SC_YQ111', 'cdna_bam_name',
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
            ),
            ('SC_YQ111', 'cdn_bam_name',
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
    @patch('accessors.sample_control_accessor.SampleControlAccessor')
    @patch('accessors.s3_accessor.S3Accessor.get_download_url')
    def test_get_file_url(self, molecular_id, file_name, item, get_download_url_return, expect_return,
                          get_download_url_function, mock_scAccessor_class):
        get_download_url_function.return_value = get_download_url_return
        instance = mock_scAccessor_class.return_value
        instance.get_item.return_value = item

        try:
            s3_url = SequenceFile().get_file_url(molecular_id, file_name)
        except Exception as e:
            print e.message
            assert e.message.find('message')
        else:
            assert(s3_url['s3_download_file_url'] == expect_return)

if __name__ == '__main__':
    unittest.main()
