import unittest
from mock import patch
from ddt import ddt, data, unpack
import app
import json


@ddt
@patch('resources.generic_file.SampleControlAccessor')
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
    @patch('resources.generic_file.S3Accessor')
    def test_get_file_url(self, molecular_id, file_format, nucleic_acid_type, item, get_download_url_return,
                          expect_return, mock_s3_accessor, mock_sc_accessor):
        s3_instance = mock_s3_accessor.return_value
        s3_instance.get_download_url.return_value = get_download_url_return
        instance = mock_sc_accessor.return_value
        instance.get_item.return_value = item

        if nucleic_acid_type is None:
            return_value = self.app.get('/api/v1/sample_controls/sequence_files/' + molecular_id + '/' + file_format)
        else:
            return_value = self.app.get(
                '/api/v1/sample_controls/sequence_files/' + molecular_id + '/' + file_format + '/' + nucleic_acid_type)

        assert (json.loads(return_value.data)["s3_download_file_url"] == expect_return)

    @data(
            ('SC_YQ111', 'vcf', None),
            ('SC_YQ111', 'bam', 'cdna')
        )
    @unpack
    @patch('common.ped_match_bot.PedMatchBot.send_message')
    def test_get_item_exception(self, molecular_id, file_format, nucleic_acid_type, mock_sc_accessor, mock_log_abort):
        instance = mock_sc_accessor.return_value
        instance.get_item.side_effect = Exception('Testing get_item exception')
        mock_log_abort.return_value = True
        if nucleic_acid_type is None:
            return_value = self.app.get('/api/v1/sample_controls/sequence_files/' + molecular_id + '/' + file_format)
        else:
            return_value = self.app.get(
                '/api/v1/sample_controls/sequence_files/' + molecular_id + '/' + file_format + '/' + nucleic_acid_type)
        print return_value.data
        print return_value.status_code
        assert return_value.status_code == 500
        assert "get_item failed" in return_value.data

    @data(
            ('SC_YQ111', 'vcf', None,
             {'site_ip_address': '129.43.127.133',
              'control_type': 'no_template',
              'site': 'mocha',
              'vcf_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_v2.vcf',
              'date_molecular_id_created': '2016-08-28 16:56:29.333',
              'molecular_id': 'SC_YQ111',
              'analysis_id': 'SC_YQ111_SC_YQ111_k123_v1'}),
            ('SC_YQ111', 'bam', 'cdna',
             {'site_ip_address': '129.43.127.133',
              'control_type': 'no_template',
              'site': 'mocha',
              'cdna_bam_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam',
              'date_molecular_id_created': '2016-08-28 16:56:29.333',
              'molecular_id': 'SC_YQ111',
              'analysis_id': 'SC_YQ111_SC_YQ111_k123_v1'})
         )
    @unpack
    @patch('resources.generic_file.S3Accessor')
    def test_get_file_url_exception(self, molecular_id, file_format, nucleic_acid_type, item,
                                    mock_s3_accessor, mock_sc_accessor):
        s3_instance = mock_s3_accessor.return_value
        s3_instance.get_download_url.side_effect = Exception('Testing get_download_url exception')
        instance = mock_sc_accessor.return_value
        instance.get_item.return_value = item

        if nucleic_acid_type is None:
            return_value = self.app.get('/api/v1/sample_controls/sequence_files/' + molecular_id + '/' + file_format)
        else:
            return_value = self.app.get(
                '/api/v1/sample_controls/sequence_files/' + molecular_id + '/' + file_format + '/' + nucleic_acid_type)

        assert return_value.status_code == 500
        assert "Testing get_download_url exception" in return_value.data

    @data(
            ('SC_YQ111', 'tsv', None,
             {'site_ip_address': '129.43.127.133',
              'control_type': 'no_template',
              'site': 'mocha',
              'tsv_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_v2.tsv',
              'cdna_bai_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bai',
              'date_molecular_id_created': '2016-08-28 16:56:29.333',
              'molecular_id': 'SC_YQ111',
              'analysis_id': 'SC_YQ111_SC_YQ111_k123_v1'
              }
             ),
            ('SC_YQ111', 'bai', 'cdna',
             {'site_ip_address': '129.43.127.133',
              'control_type': 'no_template',
              'site': 'mocha',
              'tsv_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_v2.tsv',
              'cdna_bai_name': 'mocha/SC_YQ111/SC_YQ111_SC_YQ111_k123_v1/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bai',
              'date_molecular_id_created': '2016-08-28 16:56:29.333',
              'molecular_id': 'SC_YQ111',
              'analysis_id': 'SC_YQ111_SC_YQ111_k123_v1'
              }
             )
        )
    @unpack
    @patch('resources.generic_file.S3Accessor')
    def test_get_file_url_key_error_exception(self, molecular_id, file_format, nucleic_acid_type, item,
                                              mock_s3_accessor, mock_sc_accessor):
        s3_instance = mock_s3_accessor.return_value
        s3_instance.get_download_url.side_effect = KeyError('Testing get_download_url s3 key')
        instance = mock_sc_accessor.return_value
        instance.get_item.return_value = item

        if nucleic_acid_type is None:
            return_value = self.app.get('/api/v1/sample_controls/sequence_files/' + molecular_id + '/' + file_format)
        else:
            return_value = self.app.get(
                '/api/v1/sample_controls/sequence_files/' + molecular_id + '/' + file_format + '/' + nucleic_acid_type)

        assert return_value.status_code == 404
        assert "Testing get_download_url s3 key" in return_value.data

# if __name__ == '__main__':
#     unittest.main()
