#!/usr/bin/env python

import os
import unittest
from collections import OrderedDict

from vcf import Vcf, VcfRecord, VcfGenotypeInformation, VcfInfoField, VcfMetadata, VcfFuncBlock
from vcf.test.base_test import BaseTestCase

include = True

class VcfRecordTestCase(BaseTestCase):
    def setUp(self):
        self.info_metadata_record = \
            '##INFO=<ID=AF,Number=A,Type=Float,Description="Strand-specific-error prediction on positive strand.">'
        self.metadata_object = VcfMetadata.create_from_metadata_record(self.info_metadata_record)
        self.info_field_dict = dict({self.metadata_object['ID']: self.metadata_object})
        self.record_string = "chr1\t43815008\tCOSM29008;COSM43212\tTGG\tTCG,AAA\t108.00\t.\t" \
                             "AF=0,0,0,0,0;FUNC=[{'normalizedAlt':'C'}]\tGT:GQ\t0/1:99"
        header_dict = {
            'CHROM': 0, 'POS': 1, 'ID': 2, 'REF': 3, 'ALT': 4, 'QUAL': 5, 'FILTER': 6, 'INFO': 7, 'FORMAT': 8, 'Samp': 9
        }

        self.header = OrderedDict(sorted(header_dict.items(), key=lambda item: item[1]))
        self.info_and_format_metadata = dict({'INFO': self.info_field_dict, 'FORMAT': {}})
        self.record = VcfRecord.create_from_record_string(
            self.record_string, self.header, self.info_and_format_metadata, 1)

    def test_set_from_record_string(self):
        parts = self.record_string.split('\t')

        self.assertEqual(self.record['CHROM'], 'chr1')
        self.assertEqual(self.record['POS'], 43815008)
        self.assertListEqual(self.record['ID'], ['COSM29008', 'COSM43212'])
        self.assertEqual(self.record['REF'], 'TGG')
        self.assertListEqual(self.record['ALT'], ['TCG', 'AAA'])
        self.assertEqual(self.record['QUAL'], '108.00')
        self.assertEqual(self.record['FILTER'], '.')

        info = VcfInfoField.create_from_info_string(parts[self.header['INFO']], self.info_field_dict)
        self.assertEqual(self.record['INFO'], info)

        genotype_info = VcfGenotypeInformation.create_from_genotype_information(
            parts[self.header['FORMAT']], parts[self.header['Samp']], self.info_and_format_metadata)
        self.assertEqual(self.record['GENOTYPE'], genotype_info)

    def test_set_from_record_string_version0_1_4(self):
        self.info_metadata_record = \
            '##INFO=<ID=AF,Number=A,Type=Float,Description="Strand-specific-error prediction on positive strand.">'
        self.metadata_object = VcfMetadata.create_from_metadata_record(self.info_metadata_record)
        self.info_field_dict = dict({self.metadata_object['ID']: self.metadata_object})
        self.record_string = "chr1\t43815008\tCOSM29008;COSM43212\tTGG\tTCG,AAA\t108.00\t.\t" \
                             "AF=0,0,0,0,0;FUNC=[{'normalizedAlt':'C'}]\tGT:GQ\t0/1:99"
        header_dict = {
            'CHROM': 0, 'POS': 1, 'ID': 2, 'REF': 3, 'ALT': 4, 'QUAL': 5, 'FILTER': 6, 'INFO': 7, 'FORMAT': 8, 'GENOTYPE': 9
        }

        self.header = OrderedDict(sorted(header_dict.items(), key=lambda item: item[1]))
        self.info_and_format_metadata = dict({'INFO': self.info_field_dict, 'FORMAT': {}})
        self.record = VcfRecord.create_from_record_string(
            self.record_string, self.header, self.info_and_format_metadata, 1)

        parts = self.record_string.split('\t')

        self.assertEqual(self.record['CHROM'], 'chr1')
        self.assertEqual(self.record['POS'], 43815008)
        self.assertListEqual(self.record['ID'], ['COSM29008', 'COSM43212'])
        self.assertEqual(self.record['REF'], 'TGG')
        self.assertListEqual(self.record['ALT'], ['TCG', 'AAA'])
        self.assertEqual(self.record['QUAL'], '108.00')
        self.assertEqual(self.record['FILTER'], '.')

        info = VcfInfoField.create_from_info_string(parts[self.header['INFO']], self.info_field_dict)
        self.assertEqual(self.record['INFO'], info)

        genotype_info = VcfGenotypeInformation.create_from_genotype_information(
            parts[self.header['FORMAT']], parts[self.header['GENOTYPE']], self.info_and_format_metadata)
        self.assertEqual(self.record['GENOTYPE'], genotype_info)

    def test_normalize_variant_information(self):
        self.assertListEqual(self.record.normalized_variant_information, [
            {'REF': 'G', 'ALT': 'C', 'POS': 43815009},
            {'REF': 'TGG', 'ALT': 'AAA', 'POS': 43815008}
        ])

    def test_str(self):
        self.assertEqual(str(self.record), self.record_string)

    def test_getitem(self):
        for field in self.record.fields:
            self.assertEqual(self.record.fields[field], self.record[field])

    def test_setitem(self):
        self.assertEqual(self.record['CHROM'], 'chr1')
        self.record['CHROM'] = 'foo'
        self.assertEqual(self.record['CHROM'], 'foo')

    def test_normalize_variant_when_ref_is_single_base(self):
        self.assertDictEqual(VcfRecord.normalize_variant('T', 'TGC', 10), {'REF': 'T', 'ALT': 'TGC', 'POS': 10})

    def test_normalize_variant_when_alt_is_single_base(self):
        self.assertDictEqual(VcfRecord.normalize_variant('TGG', 'T', 10), {'REF': 'TGG', 'ALT': 'T', 'POS': 10})

    def test_normalize_variant_when_snp_in_middle(self):
        self.assertDictEqual(VcfRecord.normalize_variant('TGG', 'TCG', 10), {'REF': 'G', 'ALT': 'C', 'POS': 11})

    def test_normalize_variant_when_snp_at_end(self):
        self.assertDictEqual(VcfRecord.normalize_variant('TGG', 'TGC', 10), {'REF': 'G', 'ALT': 'C', 'POS': 12})

    def test_normalize_variant_when_snp_at_beginning(self):
        self.assertDictEqual(VcfRecord.normalize_variant('TGG', 'AGG', 10), {'REF': 'T', 'ALT': 'A', 'POS': 10})

    def test_normalize_variant_when_insertion(self):
        self.assertDictEqual(VcfRecord.normalize_variant('ATC', 'ATCGGA', 10), {'REF': 'C', 'ALT': 'CGGA', 'POS': 12})

    def test_normalize_variant_when_deletion_at_end(self):
        self.assertDictEqual(VcfRecord.normalize_variant('ATCGGA', 'ATC', 10), {'REF': 'CGGA', 'ALT': 'C', 'POS': 12})

    def test_normalize_variant_when_deletion_at_beginning(self):
        self.assertDictEqual(VcfRecord.normalize_variant('CCGA', 'CG', 10), {'REF': 'CGA', 'ALT': 'G', 'POS': 11})

    def test_normalize_variant_when_block_substitution(self):
        self.assertDictEqual(VcfRecord.normalize_variant('ATC', 'ATGGTA', 10), {'REF': 'C', 'ALT': 'GGTA', 'POS': 12})

    def test_normalize_variant_when_no_common_bases(self):
        self.assertDictEqual(VcfRecord.normalize_variant('TGG', 'AAA', 10), {'REF': 'TGG', 'ALT': 'AAA', 'POS': 10})

    def test_trim_common_bases(self):
        self.assertEqual(VcfRecord.reverse_and_trim_common_bases_from_front('TCGA', 'TAGA'), ('CT', 'AT', 2))

class VcfInfoFieldTestCase(BaseTestCase):
    def setUp(self):
        self.info_string = 'AF=0,0,0,0,0'
        self.info_metadata_record = \
            '##INFO=<ID=AF,Number=A,Type=Float,Description="Strand-specific-error prediction on positive strand.">'
        self.metadata_object = VcfMetadata.create_from_metadata_record(self.info_metadata_record)
        self.info = VcfInfoField.create_from_info_string(
            self.info_string, dict({self.metadata_object['ID']: self.metadata_object}))

    def test_create_from_info_string(self):
        self.assertDictEqual(self.info.properties, {'AF': ['0', '0', '0', '0', '0']})

    def test_getitem(self):
        for item in self.info.properties:
            self.assertEqual(self.info.properties[item], self.info[item])

    def test_is_per_allele_when_true(self):
        self.assertTrue(self.info.is_per_allele('AF'))

    def test_str(self):
        self.assertEqual(str(self.info), self.info_string)

class VcfGenotypeInformationTestCase(BaseTestCase):
    def setUp(self):
        self.format_string = 'GT:GQ'
        self.genotype_information_string = '0/1:99'
        self.vcf_object = Vcf()
        self.vcf_object.info_and_format_metadata['FORMAT']['AF'] = VcfMetadata.create_from_metadata_record(
            '##FORMAT=<ID=AF,Number=A,Type=Float,Description="Allele frequency based on Flow Evaluator observation counts">')
        self.vcf_object.info_and_format_metadata['FORMAT']['GQ'] = VcfMetadata.create_from_metadata_record(
            '##FORMAT=<ID=GQ,Number=1,Type=Integer,Description="Genotype Quality, the Phred-scaled marginal (or unconditional) probability of the called genotype">')
        self.vcf_object.info_and_format_metadata['FORMAT']['GT'] = VcfMetadata.create_from_metadata_record(
            '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">')
        self.genotype_info = VcfGenotypeInformation.create_from_genotype_information(
            self.format_string,
            self.genotype_information_string,
            self.vcf_object.info_and_format_metadata['FORMAT']
        )

    def test_create_from_genotype_information(self):
        self.assertDictEqual(self.genotype_info.properties, {'GT': ['0/1'], 'GQ': ['99']})

    def test_as_format_string(self):
        self.assertEqual(self.genotype_info.as_format_string(), self.format_string)

    def test_as_genotype_info_string(self):
        self.assertEqual(self.genotype_info.as_genotype_info_string(), self.genotype_information_string)

    def is_per_allele_when_per_allele(self):
        self.assertTrue(self.genotype_info.is_per_allele('AF'))

    def is_per_allele_when_not_per_allele(self):
        self.assertFalse(self.genotype_info.is_per_allele('GT'))

    def test_str(self):
        self.assertEqual(str(self.genotype_info), '\t'.join([self.format_string, self.genotype_information_string]))

    def test_getitem(self):
        for item in self.genotype_info.properties:
            self.assertEqual(self.genotype_info.properties[item], self.genotype_info[item])

class VcfFuncBlockTestCase(BaseTestCase):
    def setUp(self):
        self.func_string = "[{'normalizedAlt':'C','normalizedRef':'G','normalizedPos':'43815009'," \
                           "'transcript':'NM_005373.2','gene':'MPL','location':'exonic','exon':'10'}]"
        self.func_block = VcfFuncBlock.create_from_func_string(self.func_string)

    def test_create_from_func_string(self):
        self.assertListEqual(self.func_block.funcs, [{
            'normalizedAlt': 'C',
            'normalizedRef': 'G',
            'normalizedPos': 43815009,
            'transcript': 'NM_005373.2',
            'gene': 'MPL',
            'location': 'exonic',
            'exon': 10
        }])

    def test_getitem(self):
        for index, item in enumerate(self.func_block.funcs):
            self.assertDictEqual(self.func_block.funcs[index], self.func_block[index])

    def test_str(self):
        self.assertEqual(str(self.func_block), self.func_string)

class VcfMetadataTestCase(BaseTestCase):
    def setUp(self):
        self.info_metadata_record = \
            '##INFO=<ID=SSEP,Number=A,Type=Float,Description="Strand-specific-error prediction on positive strand.">'
        self.format_metadata_record = \
            '##FORMAT=<ID=CN,Number=1,Type=Float,Description="Copy number genotype for imprecise events">'
        self.info_metadata = VcfMetadata.create_from_metadata_record(self.info_metadata_record)
        self.format_metadata = VcfMetadata.create_from_metadata_record(self.format_metadata_record)

    def test_create_from_metadata_record_when_info_metadata(self):
        self.assertEqual(self.info_metadata.metadata_type, 'INFO')
        self.assertDictEqual(self.info_metadata.properties, {
            'ID': 'SSEP',
            'Number': 'A',
            'Type': 'Float',
            'Description': '"Strand-specific-error prediction on positive strand."'
        })

    def test_create_from_metadata_record_when_format_metadata(self):
        self.assertEqual(self.format_metadata.metadata_type, 'FORMAT')
        self.assertDictEqual(self.format_metadata.properties, {
            'ID': 'CN',
            'Number': '1',
            'Type': 'Float',
            'Description': '"Copy number genotype for imprecise events"'
        })

    def test_is_per_allele_when_per_allele(self):
        self.assertTrue(self.info_metadata.is_per_allele())

    def test_is_per_allele_when_not_per_allele(self):
        self.assertFalse(self.format_metadata.is_per_allele())

    def test_getitem(self):
        for item in self.info_metadata.properties:
            self.assertEqual(self.info_metadata.properties[item], self.info_metadata[item])

    def test_setitem(self):
        self.assertIsNone(self.info_metadata.properties.get('foo'))
        self.info_metadata['foo'] = 'bar'
        self.assertEqual(self.info_metadata['foo'], 'bar')

    def test_str(self):
        self.assertEqual(str(self.info_metadata), self.info_metadata_record)
        self.assertEqual(str(self.format_metadata), self.format_metadata_record)

    def test_ne(self):
        self.assertNotEqual(self.info_metadata, self.format_metadata)

    def test_eq(self):
        self.assertEqual(self.info_metadata, self.info_metadata)

    def test_set_from_metadata_record_when_multiple_equal_signs(self):
        self.format_metadata_record = \
            '##FORMAT=<ID=GL,Number=3,Type=Float,Description="Likelihoods for RR,RA,AA genotypes (R=ref,A=alt)">'
        self.format_metadata = VcfMetadata.create_from_metadata_record(self.format_metadata_record)
        self.assertEqual("GL", self.format_metadata['ID'])
        self.assertEqual("3", self.format_metadata['Number'])
        self.assertEqual('"Likelihoods for RR,RA,AA genotypes (R=ref,A=alt)"', self.format_metadata['Description'])

class VcfTestCase(BaseTestCase):
    TEST_INPUT_VCF_FILE_NAME = os.path.join(os.path.dirname(__file__), 'test_in.vcf')
    TEST_OUTPUT_VCF_FILE_NAME = None

    def setUp(self):
        self.vcf_object = Vcf()
        self.vcf_object.read_from_vcf_file(self.TEST_INPUT_VCF_FILE_NAME)
        self.TEST_OUTPUT_VCF_FILE_NAME = os.path.join(self.get_temp_output_dir(), 'test_out.vcf')

    @staticmethod
    def get_temp_output_dir():
        ovcf_test_tempdir = os.getenv('OVCF_TEST_TEMPDIR')

        if ovcf_test_tempdir is None or os.path.exists(ovcf_test_tempdir) is False:
            ovcf_test_tempdir = tempfile.mkdtemp(prefix='Oncomine_VCF_Converter_Tests_')
            os.environ['OVCF_TEST_TEMPDIR'] = ovcf_test_tempdir

        return ovcf_test_tempdir

    def test_read_from_vcf_file(self):
        self.assertEqual(len(self.vcf_object.metadata_raw), 135)
        self.assertEqual(len(self.vcf_object.sample_run_metadata), 51)
        self.assertEqual(len(self.vcf_object.info_and_format_metadata), 2)
        self.assertEqual(len(self.vcf_object.info_and_format_metadata['INFO']), 65)
        self.assertEqual(len(self.vcf_object.info_and_format_metadata['FORMAT']), 19)
        self.assertEqual(len(self.vcf_object.sample_data), 1)
        self.assertDictEqual(self.vcf_object.header, {
            'CHROM': 0, 'POS': 1, 'ID': 2, 'REF': 3, 'ALT': 4, 'QUAL': 5, 'FILTER': 6, 'INFO': 7,
            'FORMAT': 8, 'Auto_user_C13-693-Ex694_1B_OCPv4_B_33687_90078_IonXpress_001_v1': 9
        })

    def test_write_to_file(self):
        self.vcf_object.write_to_vcf_file(self.TEST_OUTPUT_VCF_FILE_NAME)
        self.assertEqual(
            open(self.TEST_INPUT_VCF_FILE_NAME, 'r').read(), open(self.TEST_OUTPUT_VCF_FILE_NAME, 'r').read())

    def test_str(self):
        self.assertEqual(str(self.vcf_object), open(self.TEST_INPUT_VCF_FILE_NAME, 'r').read())

    def test_write_to_vcf_file_raises_error_when_output_file_exists(self):
        self.assertRaises(IOError, self.vcf_object.write_to_vcf_file, self.TEST_INPUT_VCF_FILE_NAME)

    def tearDown(self):
        if os.path.isfile(self.TEST_OUTPUT_VCF_FILE_NAME):
            os.remove(self.TEST_OUTPUT_VCF_FILE_NAME)

if __name__ == '__main__':
    unittest.main()