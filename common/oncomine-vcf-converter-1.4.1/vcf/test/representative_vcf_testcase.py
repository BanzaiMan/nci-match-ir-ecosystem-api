#!/usr/bin/env python

import os
import re
import csv
import unittest


from base_test import BaseTestCase
from vcf import Vcf, VcfConverter

include = True

class RepresentativeVcfTestCase(BaseTestCase):
    REPRESENTATIVE_TESTING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'representative_vcf_testing')
    INPUT_DIR = os.path.join(REPRESENTATIVE_TESTING_DIR, 'input')
    TEST_INPUT_FILE_NAME = None
    TEST_OUTPUT_FILE_NAME = None
    FILE_PARAM = None
    VCF_FILE_VERSION = None
    FUSION_TYPES = {'Fusion', '5p3pAssays', 'ExprControl'}

    @classmethod
    def setUpClass(cls):
        print 'INPUT_DIR:', cls.INPUT_DIR
        super(RepresentativeVcfTestCase, cls).setUpClass()
        cls.TEST_INPUT_FILE_NAME = os.path.join(cls.INPUT_DIR, cls.VCF_FILE_VERSION, cls.FILE_PARAM)
        cls.TEST_OUTPUT_FILE_NAME = os.path.join(cls.OUTPUT_DIR, cls.VCF_FILE_VERSION, cls.FILE_PARAM.replace('.vcf','.txt'))

        final_output_dir = os.path.join(cls.OUTPUT_DIR, cls.VCF_FILE_VERSION)
        if not os.path.exists(final_output_dir):
            os.makedirs(final_output_dir)

        vcf_obj = Vcf.create_from_vcf_file(cls.TEST_INPUT_FILE_NAME)
        converter = VcfConverter()
        vcf_records = converter.convert(vcf_obj)
        converter.write_to_file(cls.TEST_OUTPUT_FILE_NAME, vcf_records, vcf_obj.metadata_raw, [], [])
        reader = csv.DictReader(open(cls.TEST_OUTPUT_FILE_NAME, 'r'), delimiter='\t')
        cls.records = [record for record in reader]
        cls.columns = reader.fieldnames
        cls.column_to_unique_values = {
            key: set([record[key] for record in cls.records]) for key in cls.columns
        }

    def test_each_record_has_index(self):
        for record in self.records:
            self.assertIsNotNone(record['vcf.rownum'], 'Index not found for at least one record!')
            self.assertNotEqual('', record['vcf.rownum'], 'Index not found for at least one record!')

    def test_each_record_has_rowtype(self):
        for record in self.records:
            self.assertIsNotNone(
                record['rowtype'], 'rowtype was not set for record {record}'.format(record=record['vcf.rownum']))
            self.assertNotEqual(
                '', record['rowtype'], 'rowtype was not set for record {record}'.format(record=record['vcf.rownum']))

    def test_all_rowtypes_in_expected_set(self):
        for rowtype in self.column_to_unique_values['rowtype']:
            self.assertIn(
                rowtype, {'ExprControl', '5p3pAssays', 'Fusion', 'CNV', 'ins', 'del', 'snp', 'mnp', 'complex'},
                'rowtype was unexpected value {value} for at least one record'.format(value=rowtype))

    def test_rowtype_equals_svtype_when_svtype_set(self):
        for record in self.records:
            record_svtype = record.get('INFO.1.SVTYPE')
            if record_svtype:
                self.assertEqual(
                    record_svtype, record['rowtype'],
                    'rowtype was {rowtype} but SVTYPE was {svtype} for record {record}'.format(
                        rowtype=record['rowtype'], svtype=record_svtype, record=record['vcf.rownum']
                    ))

    def test_rowtype_equals_type_when_svtype_unset(self):
        for record in self.records:
            if not record.get('INFO.1.SVTYPE'):
                self.assertEqual(
                    record['INFO.A.TYPE'], record['rowtype'],
                    'rowtype was {rowtype} but TYPE was {type} for record {record}'.format(
                        rowtype=record['rowtype'], type=record['INFO.A.TYPE'], record=record['vcf.rownum']
                    ))

    def test_each_record_has_call(self):
        self.assertFalse('' in self.column_to_unique_values['call'], 'call was not set for at least one record')

    def test_all_calls_in_expected_set(self):
        for call in self.column_to_unique_values['call']:
            self.assertIn(
                call, {'POS', 'NEG', 'AMP', 'DEL', 'NOCALL'},
                'call was unexpected value {value} for at least one record'.format(
                    value=call
                )
            )

    def test_call_is_pos_for_fusion_records_when_filter_is_pass(self):
        for record in self.records:
            record_svtype = record.get('INFO.1.SVTYPE')
            if record_svtype in self.FUSION_TYPES and record['FILTER'] == 'PASS':
                self.assertEqual(
                    'POS', record['call'], 'call was {call} but should have been POS for record {record}'.format(
                        call=record['call'], record=record['vcf.rownum']))

    def test_call_is_neg_for_fusion_records_when_filter_is_dot(self):
        for record in self.records:
            record_svtype = record.get('INFO.1.SVTYPE')
            if record_svtype in self.FUSION_TYPES and record['FILTER'] == '.':
                self.assertEqual(
                    'NEG', record['call'], 'call was {call} but should have been NEG for record {record}'.format(
                        call=record['call'], record=record['vcf.rownum']))

    def test_call_is_amp_for_cnv_records_when_ci_zero_point_zero_five_greater_than_or_equal_to_four(self):
        for record in self.records:
            record_svtype = record.get('INFO.1.SVTYPE')
            if record_svtype == 'CNV':
                ci_values = dict(item.split(':') for item in record['INFO...CI'].split(','))
                if float(ci_values['0.05']) >= 4:
                    self.assertEqual(
                        'AMP', record['call'], 'call was {call} but should have been AMP for record {record}'.format(
                            call=record['call'], record=record['vcf.rownum']))

    def test_call_is_del_for_cnv_records_when_ci_zero_point_nine_five_less_than_or_equal_to_one(self):
        for record in self.records:
            record_svtype = record.get('INFO.1.SVTYPE')
            if record_svtype == 'CNV':
                ci_values = dict(item.split(':') for item in record['INFO...CI'].split(','))
                if float(ci_values['0.95']) <= 1:
                    self.assertEqual(
                        'DEL', record['call'], 'call was {call} but should have been DEL for record {record}'.format(
                            call=record['call'], record=record['vcf.rownum']))

    def test_call_is_neg_for_cnv_records_when_ci_values_match_both_or_neither_condition(self):
        for record in self.records:
            record_svtype = record.get('INFO.1.SVTYPE')
            if record_svtype == 'CNV':
                ci_values = dict(item.split(':') for item in record['INFO...CI'].split(','))
                five_percent = ci_values['0.05']
                ninety_five_percent = ci_values['0.95']
                if float(five_percent) < 4 and float(ninety_five_percent) > 1 or \
                   float(five_percent) >= 4 and float(ninety_five_percent) <= 1:
                    self.assertEqual(
                        'NEG', record['call'], 'call was {call} but should have been NEG for record {record}'.format(
                            call=record['call'], record=record['vcf.rownum']))

    def test_call_is_nocall_when_svtype_unset_and_genotype_nocall(self):
        for record in self.records:
            record_svtype = record.get('INFO.1.SVTYPE')
            if not record_svtype and record['FORMAT.1.GT'] == './.':
                self.assertEqual(
                    'NOCALL', record['call'], 'call was {call} but should have been NOCALL for record {record}'.format(
                        call=record['call'], record=record['vcf.rownum']))

    def test_call_is_pos_when_svtype_unset_and_alt_matches_genotype(self):
        for record in self.records:
            record_svtype = record.get('INFO.1.SVTYPE')
            if not record_svtype:
                alt_index = record['ALT.idx']
                alt_one, alt_two = record['FORMAT.1.GT'].split('/')
                if alt_one != '.' and alt_two != '.' and (alt_index == alt_one or alt_index == alt_two):
                    self.assertEqual(
                        'POS', record['call'], 'call was {call} but should have been POS for record {record}'.format(
                            call=record['call'], record=record['vcf.rownum']))

    def test_call_is_neg_when_svtype_unset_and_alt_does_not_match_genotype(self):
        for record in self.records:
            record_svtype = record.get('INFO.1.SVTYPE')
            if not record_svtype:
                alt_index = record['ALT.idx']
                alt_one, alt_two = record['FORMAT.1.GT'].split('/')
                if alt_one != '.' and alt_two != '.' and alt_index != alt_one and alt_index != alt_two:
                    self.assertEqual(
                        'NEG', record['call'], 'call was {call} but should have been NEG for record {record}'.format(
                            call=record['call'], record=record['vcf.rownum']))

    def test_each_record_has_id_count(self):
        self.assertFalse('' in self.column_to_unique_values['ID.count'], 'ID.count was not set for at least one record')

    def test_each_record_has_alt_count(self):
        self.assertFalse(
            '' in self.column_to_unique_values['ALT.count'], 'ALT.count was not set for at least one record')

    def test_oid_count_unset_when_svtype_set(self):
        for record in self.records:
            if record.get('INFO.1.SVTYPE'):
                self.assertEqual(
                    '', record['OID.count'], 'OID.count was set for non-TVC record {record}'.format(
                        record=record['vcf.rownum']
                    )
                )

    def test_each_record_has_func_count(self):
        self.assertFalse(
            '' in self.column_to_unique_values['FUNC.count'], 'FUNC.count was not set for at least one record')

    def test_each_record_has_alt_idx(self):
        self.assertFalse('' in self.column_to_unique_values['ALT.idx'], 'ALT.idx was not set for at least one record')

    def test_each_record_has_nonzero_alt_idx(self):
        self.assertFalse('0' in self.column_to_unique_values['ALT.idx'], 'ALT.idx was 0 for at least one record')

    def test_oid_idx_unset_when_svtype_set(self):
        for record in self.records:
            if record.get('INFO.1.SVTYPE'):
                self.assertEqual('', record['OID.idx'], 'OID.idx was set for non-TVC record {record}'.format(
                    record=record['vcf.rownum']
                ))

    def test_oid_idx_nonzero_when_svtype_unset(self):
        for record in self.records:
            if not record.get('INFO.1.SVTYPE'):
                self.assertNotEqual(
                    '0', record['OID.idx'], 'OID.idx was 0 for record {record}'.format(record=record['vcf.rownum']))

    def test_oid_idx_set_when_svtype_unset(self):
        for record in self.records:
            if not record.get('INFO.1.SVTYPE'):
                self.assertNotEqual('', record['OID.idx'], 'OID.idx was not set for TVC record {record}'.format(
                    record=record['vcf.rownum']
                ))

    def test_each_record_has_chrom(self):
        self.assertFalse('' in self.column_to_unique_values['CHROM'], 'CHROM was not set for at least one record')

    def test_each_record_has_pos(self):
        self.assertFalse('' in self.column_to_unique_values['POS'], 'POS was not set for at least one record')

    def test_each_record_has_id(self):
        self.assertFalse('' in self.column_to_unique_values['ID'], 'ID was not set for at least one record')

    def test_each_record_has_ref(self):
        self.assertFalse('' in self.column_to_unique_values['REF'], 'REF was not set for at least one record')

    def test_each_record_has_alt(self):
        self.assertFalse('' in self.column_to_unique_values['ALT'], 'ALT was not set for at least one record')

    def test_alt_is_cnv_when_svtype_is_cnv(self):
        for record in self.records:
            if record.get('INFO.1.SVTYPE') == 'CNV':
                self.assertEqual('<CNV>', record['ALT'], 'ALT value was not <CNV> for CNV record {record}'.format(
                    record=record['vcf.rownum']
                ))

    def test_info_field_numbers_in_expected_set(self):
        for column in self.column_to_unique_values:
            if column.startswith('INFO'):
                info, rest = column.split('.', 1)
                self.failUnless(rest[0].isdigit() or rest[0] in {'A', '.'}, '{info} had unexpected number'.format(
                    info=column
                ))

    def test_info_fields_have_three_parts(self):
        for column in self.column_to_unique_values:
            if column.startswith('INFO'):
                items = column.split('.')
                self.failUnless(
                    len(items) == 3 or len(items) == 4 and '...' in column,
                    '{info} did not match format INFO.<number>.<property>'.format(info=column)
                )

    def test_info_zero_columns_are_true_or_false_only(self):
        for column in self.column_to_unique_values:
            if column.startswith('INFO.0.'):
                for value in self.column_to_unique_values[column]:
                    self.assertIn(value, {'True', 'False'}, '{info} was unexpected value {value}'.format(
                        info=column, value=value
                    ))

    def test_cdf_ld_unset_when_svtype_not_cnv(self):
        for record in self.records:
            if record.get('INFO.1.SVTYPE') != 'CNV':
                self.failUnless(
                    record.get('INFO...CDF_LD') is None or record['INFO...CDF_LD'] == '',
                    'CDF_LD set for non-CNV record {record}'.format(record=record['vcf.rownum'])
                )

    def test_cdf_ld_set_when_svtype_cnv(self):
        for record in self.records:
            if record.get('INFO.1.SVTYPE') == 'CNV':
                self.assertIsNotNone(
                    record['INFO...CDF_LD'], 'CDF_LD not set for CNV record {record}'.format(record=record['vcf.rownum']))
                self.assertNotEqual('', record['INFO...CDF_LD'], 'CDF_LD not set for CNV record {record}'.format(
                    record=record['vcf.rownum'])
                )

    def test_cdf_mapd_unset_when_svtype_not_cnv(self):
        for record in self.records:
            if record.get('INFO.1.SVTYPE') != 'CNV':
                self.failUnless(
                    record.get('INFO...CDF_MAPD') is None or record['INFO...CDF_MAPD'] == '',
                    'CDF_MAPD set for non-CNV record {record}'.format(record=record['vcf.rownum'])
                )

    def test_cdf_mapd_set_when_svtype_cnv(self):
        for record in self.records:
            if record.get('INFO.1.SVTYPE') == 'CNV':
                self.assertIsNotNone(record['INFO...CDF_MAPD'], 'CDF_MAPD not set for CNV record {record}'.format(
                    record=record['vcf.rownum']))
                self.assertNotEqual('', record['INFO...CDF_MAPD'], 'CDF_MAPD not set for CNV record {record}'.format(
                    record=record['vcf.rownum']))

    def test_ci_unset_when_svtype_not_cnv(self):
        for record in self.records:
            if record.get('INFO.1.SVTYPE') != 'CNV':
                self.failUnless(
                    record.get('INFO...CI') is None or record['INFO...CI'] == '',
                    'CI set for non-CNV record {record}'.format(record=record['vcf.rownum'])
                )

    def test_ci_set_when_svtype_cnv(self):
        for record in self.records:
            if record.get('INFO.1.SVTYPE') == 'CNV':
                self.assertIsNotNone(
                    record['INFO...CI'], 'CI not set for CNV record {record}'.format(record=record['vcf.rownum']))
                self.assertNotEqual('', record['INFO...CI'], 'CI not set for CNV record {record}'.format(
                    record=record['vcf.rownum']))

    def test_each_record_has_len(self):
        for record in self.records:
            if record.get('INFO.1.SVTYPE') not in self.FUSION_TYPES:
                self.assertIsNotNone(record['INFO...LEN'], 'LEN not set for record {record}'.format(
                    record=record['vcf.rownum']))
                self.assertNotEqual('', record['INFO...LEN'], 'LEN not set for record {record}'.format(
                    record=record['vcf.rownum'])
                )

    def test_oalt_set_for_tvc_records(self):
        for record in self.records:
            if not record.get('INFO.1.SVTYPE'):
                self.assertIsNotNone(record['INFO...OALT'], 'OALT not set for record {record}'.format(
                    record=record['vcf.rownum']))
                self.assertNotEqual('', record['INFO...OALT'], 'OALT not set for record {record}'.format(
                    record=record['vcf.rownum']))

    def test_oalt_unset_for_non_tvc_records(self):
        for record in self.records:
            if record.get('INFO.1.SVTYPE'):
                self.failUnless(
                    record.get('INFO...OALT') is None or record['INFO...OALT'] == '',
                    'OALT set for non-TVC record {record}'.format(record=record['vcf.rownum'])
                )

    def test_oid_set_for_tvc_records(self):
        for record in self.records:
            if not record.get('INFO.1.SVTYPE'):
                self.assertIsNotNone(record['INFO...OID'], 'LEN not set for record {record}'.format(
                    record=record['vcf.rownum']))
                self.assertNotEqual('', record['INFO...OID'], 'LEN not set for record {record}'.format(
                    record=record['vcf.rownum']))

    def test_oid_unset_for_non_tvc_records(self):
        for record in self.records:
            if record.get('INFO.1.SVTYPE'):
                self.failUnless(
                    record.get('INFO...OID') is None or record['INFO...OID'] == '',
                    'OID set for non-TVC record {record}'.format(record=record['vcf.rownum'])
                )

    def test_omapalt_set_for_tvc_records(self):
        for record in self.records:
            if not record.get('INFO.1.SVTYPE'):
                self.assertIsNotNone(record['INFO...OMAPALT'], 'OMAPALT not set for TVC record {record}'.format(
                    record=record['vcf.rownum']))
                self.assertNotEqual('', record['INFO...OMAPALT'], 'OMAPALT not set for TVC record {record}'.format(
                    record=record['vcf.rownum']))

    def test_omapalt_unset_for_non_tvc_records(self):
        for record in self.records:
            if record.get('INFO.1.SVTYPE'):
                self.failUnless(
                    record.get('INFO...OMAPALT') is None or record['INFO...OMAPALT'] == '',
                    'OMAPALT set for non-TVC record {record}'.format(record=record['vcf.rownum'])
                )

    def test_omapalt_equals_alt_for_tvc_records(self):
        for record in self.records:
            if not record.get('INFO.1.SVTYPE'):
                self.assertEqual(
                    record['ALT'], record['INFO...OMAPALT'],
                    'OMAPALT was not equal to ALT for record {record}'.format(record=record['vcf.rownum'])
                )

    def test_opos_set_for_tvc_records(self):
        for record in self.records:
            if not record.get('INFO.1.SVTYPE'):
                self.assertIsNotNone(
                    record['INFO...OPOS'], 'OPOS was unset for TVC record {record}'.format(record=record['vcf.rownum']))
                self.assertNotEqual(
                    '', record['INFO...OPOS'], 'OPOS was unset for TVC record {record}'.format(record=record['vcf.rownum']))

    def test_opos_unset_for_non_tvc_records(self):
        for record in self.records:
            if record.get('INFO.1.SVTYPE'):
                self.failUnless(record.get('INFO...OPOS') is None or record['INFO...OPOS'] == '',
                                'OPOS was unset for TVC record {record}'.format(record=record['vcf.rownum']))

    def test_oref_set_for_tvc_records(self):
        for record in self.records:
            if not record.get('INFO.1.SVTYPE'):
                self.assertIsNotNone(
                    record['INFO...OREF'], 'OREF was unset for record {record}'.format(record=record['vcf.rownum']))
                self.assertNotEqual(
                    '', record['INFO...OREF'], 'OREF was unset for record {record}'.format(record=record['vcf.rownum']))

    def test_oref_unset_for_non_tvc_records(self):
        for record in self.records:
            if record.get('INFO.1.SVTYPE'):
                self.failUnless(record.get('INFO...OREF') is None or record['INFO...OREF'] == '',
                                'OREF was set for non-TVC record {record}'.format(record=record['vcf.rownum']))

    def test_read_count_set_for_fusion_records(self):
        for record in self.records:
            if record.get('INFO.1.SVTYPE') in self.FUSION_TYPES:
                self.failIf(
                    record.get('INFO...READ_COUNT') is None or record['INFO...READ_COUNT'] == '',
                    'READ_COUNT was not set for fusion record {record}'.format(record=record['vcf.rownum']))

    def test_read_count_unset_for_non_fusion_records(self):
        for record in self.records:
            record_svtype = record.get('INFO.1.SVTYPE')
            if record_svtype is None or record_svtype not in self.FUSION_TYPES:
                self.failUnless(
                    record.get('INFO...READ_COUNT') is None or record['INFO...READ_COUNT'] == '',
                    'READ_COUNT was set for non-fusion record {record}'.format(record=record['vcf.rownum'])
                )

    def test_each_record_has_hs(self):
        for record in self.records:
            if 'HS' in record:
                self.assertIn(
                    record['HS'], {'True', 'False'}, 'HS had enexpected value {value} in record {record}'.format(
                        value=record['HS'], record=record['vcf.rownum']
                    ))

    def test_novel_false_for_non_fusion_records(self):
        for record in self.records:
            if not record.get('INFO.1.SVTYPE') in self.FUSION_TYPES:
                self.failUnless(
                    record.get('INFO.0.NOVEL') is None or record['INFO.0.NOVEL'] == 'False',
                    'NOVEL was True for non-fusion record {record}'.format(record=record['vcf.rownum'])
                )

    def test_novel_only_contains_true_or_false(self):
        values = self.column_to_unique_values.get('INFO.0.NOVEL')
        if values is not None:
            for value in values:
                self.assertIn(value, {'True', 'False'}, 'NOVEL had unexpected value {value}'.format(value=value))

    def test_5p_3p_assays_unset_for_non_5p3passays_records(self):
        for record in self.records:
            if record.get('INFO.1.SVTYPE') != '5p3pAssays':
                self.failUnless(
                    record.get('INFO.1.5P_3P_ASSAYS') is None or record['INFO.1.5P_3P_ASSAYS'] == '',
                    '5P_3P_ASSAYS was set for record {record} but the record was not of type 5p3pAssays'.format(
                        record=record['vcf.rownum']
                    ))

    def test_annotation_unset_for_non_fusion_records(self):
        for record in self.records:
            if not record.get('INFO.1.SVTYPE') in self.FUSION_TYPES:
                self.failUnless(
                    record.get('INFO.1.ANNOTATION') is None or record['INFO.1.ANNOTATION'] == '',
                    'ANNOTATION was set for record {record} but the record was not one of the fusion types'.format(
                        record=record['vcf.rownum']
                    ))

    def test_exon_num_unset_for_non_fusion_records(self):
        for record in self.records:
            if record.get('INFO.1.SVTYPE') != 'Fusion':
                self.failUnless(
                    record.get('INFO.1.EXON_NUM') is None or record['INFO.1.EXON_NUM'] == '',
                    'EXON_NUM was set for record {record} but the record was not of type \'Fusion\''.format(
                        record=record['vcf.rownum']
                    ))

    def test_gene_name_unset_for_non_fusion_records(self):
        for record in self.records:
            if not record.get('INFO.1.SVTYPE') in self.FUSION_TYPES:
                self.failUnless(
                    record.get('INFO.1.GENE_NAME') is None or record['INFO.1.GENE_NAME'] == '',
                    'GENE_NAME was set for record {record} but the record was not one of the fusion types'.format(
                        record=record['vcf.rownum']
                    )
                )

    def test_numtiles_unset_for_non_cnv_records(self):
        for record in self.records:
            if record.get('INFO.1.SVTYPE') != 'CNV':
                self.failUnless(
                    record.get('INFO.1.NUMTILES') is None or record['INFO.1.NUMTILES'] == '',
                    'NUMTILES was set for record {record} but the record was not of type CNV'.format(
                        record=record['vcf.rownum']
                    )
                )

    def test_svtype_in_expected_set(self):
        for record in self.records:
            record_svtype = record.get('INFO.1.SVTYPE')
            if record_svtype:
                self.assertIn(
                    record_svtype, {'CNV', 'Fusion', '5p3pAssays', 'ExprControl'},
                    'Record {record} had unexpected SVTYPE {svtype}'.format(
                        record=record['vcf.rownum'], svtype=record_svtype
                    )
                )

    def test_three_prime_pos_unset_for_non_5p3passays_records(self):
        for record in self.records:
            if record.get('INFO.1.SVTYPE') != '5p3pAssays':
                self.failUnless(
                    record.get('INFO.1.THREE_PRIME_POS') is None or record['INFO.1.THREE_PRIME_POS'] == '',
                    'THREE_PRIME_POS was set for record {record} but the record was not of type 5p3pAssays'.format(
                        record=record['vcf.rownum']
                    )
                )

    def test_type_unset_when_svtype_set(self):
        for record in self.records:
            if record.get('INFO.1.SVTYPE'):
                self.failUnless(
                    record.get('INFO.A.TYPE') is None or record['INFO.A.TYPE'] == '',
                    'TYPE was set for record {record} even though SVTYPE was also set.'.format(
                        record=record['vcf.rownum']
                    )
                )

    def test_format_field_numbers_in_expected_set(self):
        for column in self.column_to_unique_values:
            if column.startswith('FORMAT'):
                info, rest = column.split('.', 1)
                self.failUnless(rest[0].isdigit() or rest[0] in {'A', '.'}, '{column} has unexpected number'.format(
                    column=column
                ))

    def test_format_fields_have_three_parts(self):
        for column in self.column_to_unique_values:
            if column.startswith('FORMAT'):
                items = column.split('.')
                self.failUnless(
                    len(items) == 3 or len(items) == 4 and '...' in column,
                    '{column} does not have 3 parts'.format(
                        column=column
                    )
                )

    def test_func_index_is_nonzero(self):
        for column in self.column_to_unique_values:
            if column.startswith('FUNC'):
                self.assertFalse(column.startswith('FUNC0.'), '{column} appears to use 0s-based indexing'.format(
                    column=column
                ))

    def test_func_columns_follow_format(self):
        for column in self.column_to_unique_values:
            if column.startswith('FUNC') and column != 'FUNC.count':
                self.assertTrue(
                    re.match('FUNC\d+.\w+', column),
                    '{column} does not match pattern FUNC<index>.<property>'.format(
                        column=column
                    )
                )

    def test_id_equals_oid(self):
        for record in self.records:
            if not record.get('INFO.1.SVTYPE'):
                self.assertEqual(
                    record['ID'], record['INFO...OID'], 'ID was not equal to OID for record {record}'.format(
                        record=record['vcf.rownum']
                    )
                )

    def test_max_oid_idx_equals_oid_count(self):
        rownum_to_oid_info = {}
        for record in self.records:
            if not record.get('INFO.1.SVTYPE'):
                oid_info = rownum_to_oid_info.get(record['vcf.rownum'])
                if not oid_info or int(record['OID.idx']) > int(oid_info[0]):
                    rownum_to_oid_info[record['vcf.rownum']] = (record['OID.idx'], record['OID.count'])
        for rownum, oid_info in rownum_to_oid_info.items():
            self.assertEqual(
                oid_info[0], oid_info[1], 'max(OID.idx) ({max}) != OID.count ({count}) for record {record}'.format(
                    max=oid_info[0], count=oid_info[1], record=rownum
                )
            )

    @classmethod
    def tearDownClass(cls):
        if os.path.isfile(cls.TEST_OUTPUT_FILE_NAME):
            os.remove(cls.TEST_OUTPUT_FILE_NAME)
