from unittest import TestCase
from mock import patch
from ddt import ddt, data, unpack
import app
import json

@ddt
@patch('resources.generic_file.SampleControlAccessor')
class TestGenericFile(TestCase):

    def setUp(self):
        self.app = app.app.test_client()
        pass

    @data(
        ('SC_SA1CB', 'qc', "u's3_download_file_url': u'https://pedmatch-dev.s3.amazonaws.com/IR_WAO85/"
                           "SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1_QC.pdf?",
         {u'ion_reporter_id': u'IR_WAO85', u'analysis_id': u'SC_SA1CB_SC_SA1CB_a888_v1',
          u'control_type': u'no_template',
          u'dna_bam_name': u'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_DNA_v1.bam',
          u'site': u'mocha',
          u'qc_name': u'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1_QC.pdf',
          u'dna_bai_name': u'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_DNA_v1.bai',
          u'cdna_bam_name': u'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_RNA_v1.bam',
          u'vcf_name': u'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.vcf',
          u'cdna_bai_name': u'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_RNA_v1.bai',
          u'date_molecular_id_created': u'2016-09-28 19:56:19.777', u'molecular_id': u'SC_SA1CB'} ,
         'https://pedmatch-dev.s3.amazonaws.com/IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis'
         '888_v1_QC.pdf?AWSAccessKeyId=AKIAJXJOWSYB5ULNEKCA&Expires=1475599059&Signature=YiKHi4QNorckhD4ipGX8zXY94RE%3D'
         , 200),
        ('SC_SA1C', 'qc', "SC_SA1C was not found.", [], '', 404),
    )
    @unpack
    @patch('resources.generic_file.S3Accessor')
    def test_get_file_url(self, molecular_id, file_type, return_message, sc_item, s3_item, returned_stat_code, mock_s3_accessor, mock_sc_accessor):
        s3_instance = mock_s3_accessor.return_value
        s3_instance.get_download_url.return_value = s3_item
        # mock_s3_accessor.return_value = s3_item

        sc_instance = mock_sc_accessor.return_value
        sc_instance.get_item.return_value = sc_item
        return_value = self.app.get('/api/v1/files/' + molecular_id + '/' + file_type)
        print return_value.status_code
        print return_message
        print str(json.loads(return_value.data))
        assert return_value.status_code == returned_stat_code
        assert return_message in str(json.loads(return_value.data))


    @data(
        ('SC_SA1CB', 'qc', "u's3_download_file_url': u'https://pedmatch-dev.s3.amazonaws.com/IR_WAO85/"
                           "SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1_QC.pdf?",
         {u'ion_reporter_id': u'IR_WAO85', u'analysis_id': u'SC_SA1CB_SC_SA1CB_a888_v1',
          u'control_type': u'no_template',
          u'dna_bam_name': u'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_DNA_v1.bam',
          u'site': u'mocha',
          u'qc_name': u'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1_QC.pdf',
          u'dna_bai_name': u'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_DNA_v1.bai',
          u'cdna_bam_name': u'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_RNA_v1.bam',
          u'vcf_name': u'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.vcf',
          u'cdna_bai_name': u'IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_RNA_v1.bai',
          u'date_molecular_id_created': u'2016-09-28 19:56:19.777', u'molecular_id': u'SC_SA1CB'},
         'https://pedmatch-dev.s3.amazonaws.com/IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis'
         '888_v1_QC.pdf?AWSAccessKeyId=AKIAJXJOWSYB5ULNEKCA&Expires=1475599059&Signature=YiKHi4QNorckhD4ipGX8zXY94RE%3D'
         , 500),
        # ('SC_SA1C', 'qc', "SC_SA1C was not found.", [], '', 404),
    )
    @unpack
    @patch('resources.generic_file.S3Accessor')
    def test_get_file_url_exception(self, molecular_id, file_type, return_message, sc_item, s3_item, returned_stat_code,
                          mock_s3_accessor, mock_sc_accessor):
        s3_instance = mock_s3_accessor.return_value
        s3_instance.get_download_url.return_value = s3_item
        # mock_s3_accessor.return_value = s3_item

        sc_instance = mock_sc_accessor.return_value
        sc_instance.get_item.side_effect = Exception('Error')
        return_value = self.app.get('/api/v1/files/' + molecular_id + '/' + file_type)
        print return_value.status_code
        print return_message
        print str(json.loads(return_value.data))
        assert return_value.status_code == returned_stat_code
        assert 'Error' in return_value.data