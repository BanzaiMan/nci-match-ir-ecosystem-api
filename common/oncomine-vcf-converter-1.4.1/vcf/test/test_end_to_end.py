import os
import unittest
import tempfile

from vcf import Vcf, VcfConverter
from vcf.test.base_test import BaseTestCase

include = True

class EndToEndTestCase(BaseTestCase):
    TEST_DIR = os.path.dirname(__file__)
    TEST_INPUT_FILE_NAME = os.path.join(TEST_DIR, 'all_data_types.vcf')
    TEST_EXPECTED_OUTPUT_FILE_NAME = os.path.join(TEST_DIR, 'expected_all_output.tsv')
    TEST_ACTUAL_OUTPUT_FILE_NAME = None

    @classmethod
    def setUpClass(cls):
        super(EndToEndTestCase, cls).setUpClass()
        cls.TEST_ACTUAL_OUTPUT_FILE_NAME = os.path.join(cls.OUTPUT_DIR, 'actual_all_output.tsv')

    def test_command_line_workflow(self):
        vcf_obj = Vcf.create_from_vcf_file(self.TEST_INPUT_FILE_NAME)
        converter = VcfConverter()
        records = converter.convert(vcf_obj)
        converter.write_to_file(self.TEST_ACTUAL_OUTPUT_FILE_NAME, records, vcf_obj.metadata_raw, [], [])

        actual_output_lines = open(self.TEST_ACTUAL_OUTPUT_FILE_NAME, 'r').readlines()
        expected_output_lines = open(self.TEST_EXPECTED_OUTPUT_FILE_NAME, 'r').readlines()

        actual_output = ''
        expected_output = ''
        for line in actual_output_lines:
            actual_output = actual_output + line.rstrip('\r\n')

        for line in expected_output_lines:
            expected_output = expected_output + line.rstrip('\r\n')

        self.assertEqual(actual_output,
                         expected_output)

    def tearDown(self):
        if os.path.exists(self.TEST_ACTUAL_OUTPUT_FILE_NAME):
            os.remove(self.TEST_ACTUAL_OUTPUT_FILE_NAME)

if __name__ == '__main__':
    EndToEndTestCase.setUpClass()
    unittest.main()
