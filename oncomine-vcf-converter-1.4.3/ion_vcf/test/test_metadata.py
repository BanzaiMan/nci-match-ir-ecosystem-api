#!/usr/bin/env python

import os
import unittest

from vcf import Vcf, VcfConverter
from vcf.test.base_test import BaseTestCase

include = True


class MetadataTestCase(BaseTestCase):
    METADATA_TESTING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'metadata_vcf_testing')
    INPUT_DIR = os.path.join(METADATA_TESTING_DIR, 'input')

    ACTUAL_OUTPUT_DIR = os.path.join(METADATA_TESTING_DIR, 'actual')
    EXPECTED_OUTPUT_DIR = os.path.join(METADATA_TESTING_DIR, 'expected')

    vcf_obj = None
    converter = None
    records = None

    @classmethod
    def setUpClass(cls):
        super(MetadataTestCase, cls).setUpClass()

        input_file_name = os.path.join(cls.INPUT_DIR, 'input.vcf')
        cls.vcf_obj = Vcf.create_from_vcf_file(input_file_name)
        cls.converter = VcfConverter()
        cls.records = cls.converter.convert(cls.vcf_obj)

    def run_test(self, expected_output_file, meta_fields):
        actual_output_path = os.path.join(self.ACTUAL_OUTPUT_DIR, expected_output_file)
        MetadataTestCase.converter.write_to_file(
            actual_output_path, self.records, self.vcf_obj.metadata_raw, meta_fields, [])
        actual_output_lines = open(actual_output_path, 'r').readlines()

        expected_output_path = os.path.join(self.EXPECTED_OUTPUT_DIR, expected_output_file)
        expected_output_lines = open(expected_output_path, 'r').readlines()

        actual_output = ''
        expected_output = ''
        for line in actual_output_lines:
            actual_output += line.rstrip('\r\n')

        for line in expected_output_lines:
            expected_output += line.rstrip('\r\n')

        self.assertEqual(
            actual_output,
            expected_output,
            'Files differ: `diff {act} {exp}'.format(act=actual_output_path, exp=expected_output_path))

    def test_no_metadata(self):
        self.run_test('no_metadata.tsv', [])

    def test_default_metadata(self):
        self.run_test('default_metadata.tsv', None)

    def test_one_metadata(self):
        self.run_test('one_metadata.tsv', ['reference'])

    def test_multiple_metadata(self):
        self.run_test('multiple_metadata.tsv', ['CellularityAsAFractionBetween0-1', 'mapd'])

    @staticmethod
    def get_files_to_convert():
        files_to_convert = []
        for path, directories, files in os.walk(os.path.join(MetadataTestCase.INPUT_DIR)):
            for vcf_file in [f for f in files if f.endswith(".vcf")]:
                files_to_convert.append(os.path.join(path, vcf_file))

        return files_to_convert


def suite():
    MetadataTestCase.setUpClass()
    return unittest.makeSuite(MetadataTestCase, 'test')

if __name__ == '__main__':
    MetadataTestCase.setUpClass()
    unittest.main()
