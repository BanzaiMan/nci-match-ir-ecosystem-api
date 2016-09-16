import unittest
from mock import patch
from ddt import ddt, data, unpack
import app
from common.sequence_file_processor import SequenceFileProcessor


@ddt
class TestSequenceFileProcessor(unittest.TestCase):

    def setUp(self):
        self.app = app.app.test_client()
        pass

    @data(('/tmp/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam', '/tmp/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bai'))
    @unpack
    @patch('common.sequence_file_processor.pysam.index')
    def test_bam_to_bai(self, bam_full_path, expected_return, mock_pysam_index_function):
        mock_pysam_index_function.return_value = True
        return_value = SequenceFileProcessor.bam_to_bai(bam_full_path)
        assert (return_value == expected_return)


    @data(('/tmp/SC_YQ111_SC_YQ111_analysis666_RNA_v2.bam', 'Testing bam to bai exception'))
    @unpack
    @patch('common.sequence_file_processor.pysam.index')
    def test_bam_to_bai_exception(self, bam_full_path, exception_message, mock_pysam_index_function):
        mock_pysam_index_function.side_effect = Exception(exception_message)
        try:
            SequenceFileProcessor.bam_to_bai(bam_full_path)
        except Exception as e:
            assert (e.message == exception_message)


    @data(  ('/tmp/SC_YQ111_SC_YQ111_analysis666_v2.vcf', '/tmp/SC_YQ111_SC_YQ111_analysis666_v2.tsv', True),
            ('/tmp/SC_YQ111_SC_YQ111_analysis666_v2.vcf', None, False)
         )
    @unpack
    @patch('common.sequence_file_processor.os.path.isfile')
    @patch('common.sequence_file_processor.os.system')
    def test_vcf_to_tsv(self, vcf_full_path, expected_return, isfile_return, mock_os_system_function, mock_os_isfile_function):
        mock_os_system_function.return_value = True
        mock_os_isfile_function.return_value = isfile_return
        return_value = SequenceFileProcessor.vcf_to_tsv(vcf_full_path)
        assert (return_value == expected_return)


    @data(('/tmp/SC_YQ111_SC_YQ111_analysis666_v2.vcf', 'Testing vcf to tsv exception'))
    @unpack
    @patch('common.sequence_file_processor.os.system')
    def test_vcf_to_tsv_exception(self, vcf_full_path, exception_message, mock_os_system_function):
        mock_os_system_function.side_effect = Exception(exception_message)
        try:
            SequenceFileProcessor.vcf_to_tsv(vcf_full_path)
        except Exception as e:
            assert (e.message == exception_message)


# if __name__ == '__main__':
#     unittest.main()
