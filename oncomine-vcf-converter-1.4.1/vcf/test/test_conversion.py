import os
import unittest

from vcf import AlleleToOriginalMapper, Vcf, VcfConverter, VcfMetadata, VcfRecord, VcfFuncBlock

include = True

class AlleleToOriginalMapperTestCase(unittest.TestCase):
    def setUp(self):
        self.mapper = AlleleToOriginalMapper()

    def test_generate_allele_to_original_map_when_same_order(self):
        alleles = ['A', 'TG', 'GCT', 'TTA']
        self.mapper.generate_allele_to_original_map(alleles, alleles)
        self.assertDictEqual(self.mapper.allele_to_original_map, {0: [0], 1: [1], 2: [2], 3: [3]})

    def test_generate_allele_to_original_map_when_all_different_order(self):
        alleles = ['A', 'TG', 'GCT', 'TTA']
        orig_alleles = ['TG', 'GCT', 'TTA', 'A']
        self.mapper.generate_allele_to_original_map(alleles, orig_alleles)
        self.assertDictEqual(self.mapper.allele_to_original_map, {0: [3], 1: [0], 2: [1], 3: [2]})

    def test_generate_allele_to_original_map_when_mixed_order(self):
        alleles = ['A', 'TG', 'GCT', 'TTA']
        orig_alleles = ['A', 'TG', 'TTA', 'GCT']
        self.mapper.generate_allele_to_original_map(alleles, orig_alleles)
        self.assertDictEqual(self.mapper.allele_to_original_map, {0: [0], 1: [1], 2: [3], 3: [2]})

    def test_getitem(self):
        alleles = ['A', 'TG', 'GCT', 'TTA']
        self.mapper.generate_allele_to_original_map(alleles, alleles)
        self.assertDictEqual(self.mapper.allele_to_original_map, {0: [0], 1: [1], 2: [2], 3: [3]})
        for key in self.mapper.allele_to_original_map:
            self.assertEqual(self.mapper.allele_to_original_map[key], self.mapper[key])

class VcfConverterTestCase(unittest.TestCase):
    TEST_INPUT_VCF_FILE_NAME = os.path.join(os.path.dirname(__file__), 'test_in.vcf')

    def setUp(self):
        self.vcf_object = Vcf.create_from_vcf_file(self.TEST_INPUT_VCF_FILE_NAME)
        self.converter = VcfConverter()
        self.vcf_header = 'CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSample'.split('\t')

    def test_normalized_info_matches_when_matches(self):
        func = {'normalizedPos': 10, 'normalizedRef': 'A', 'normalizedAlt': 'T'}
        allele = {'POS': 10, 'REF': 'A', 'ALT': 'T'}
        self.assertTrue(self.converter.normalized_info_matches(func, allele))

    def test_normalized_info_matches_when_does_not_match(self):
        func = {'normalizedPos': 10, 'normalizedRef': 'A', 'normalizedAlt': 'T'}
        allele = {'POS': 15, 'REF': 'CC', 'ALT': 'GG'}
        self.assertFalse(self.converter.normalized_info_matches(func, allele))

    def test_get_output_column_name(self):
        self.assertEqual(self.converter.get_output_column_name('INFO', self.vcf_object, 'FSAR'), 'INFO.A.FSAR')
        self.assertEqual(self.converter.get_output_column_name('FORMAT', self.vcf_object, 'CN'), 'FORMAT.1.CN')

    def test_add_format_columns_to_allele_record_with_per_variant_field_with_one_value(self):
        format_metadata = VcfMetadata.create_from_metadata_record(
            '##FORMAT=<ID=CN,Number=1,Type=Float,Description="Copy number genotype for imprecise events">')
        vcf_object = Vcf()
        vcf_object.info_and_format_metadata['FORMAT']['CN'] = format_metadata
        record = VcfRecord.create_from_record_string(
            '1\t10\tID\tT\tA\t10\t.\t\tCN\t2', self.vcf_header, vcf_object.info_and_format_metadata, 1)

        allele_record = dict()
        self.converter.add_format_columns_to_allele_record(0, allele_record, record, vcf_object)
        self.assertEqual(1, len(allele_record))
        self.assertEqual(allele_record.keys()[0], 'FORMAT.1.CN')
        self.assertEqual(allele_record.values()[0], '2')

    def test_add_format_columns_to_allele_record_with_per_variant_field_with_two_values(self):
        format_metadata = VcfMetadata.create_from_metadata_record(
            '##FORMAT=<ID=CN,Number=1,Type=Float,Description="Copy number genotype for imprecise events">')
        vcf_object = Vcf()
        vcf_object.info_and_format_metadata['FORMAT']['CN'] = format_metadata
        record = VcfRecord.create_from_record_string(
            '1\t10\tID\tT\tA\t10\t.\t\tCN\t2,5', self.vcf_header, vcf_object.info_and_format_metadata, 1)

        allele_record = dict()
        self.converter.add_format_columns_to_allele_record(0, allele_record, record, vcf_object)
        self.assertEqual(1, len(allele_record))
        self.assertEqual(allele_record.keys()[0], 'FORMAT.1.CN')
        self.assertEqual(allele_record.values()[0], '2,5')

    def test_add_format_columns_to_allele_record_with_per_allele_field_and_one_allele(self):
        format_metadata = VcfMetadata.create_from_metadata_record(
            '##FORMAT=<ID=AF,Number=A,Type=Float,Description="'
            '"Allele frequency based on Flow Evaluator observation counts">')
        vcf_object = Vcf()
        vcf_object.info_and_format_metadata['FORMAT']['AF'] = format_metadata
        record = VcfRecord.create_from_record_string(
            '1\t10\tID\tT\tA\t10\t.\t\tAF\t2', self.vcf_header, vcf_object.info_and_format_metadata, 1)

        allele_record = dict()
        self.converter.add_format_columns_to_allele_record(0, allele_record, record, vcf_object)
        self.assertEqual(1, len(allele_record))
        self.assertEqual(allele_record.keys()[0], 'FORMAT.A.AF')
        self.assertEqual(allele_record.values()[0], '2')

    def test_add_format_columns_to_allele_record_with_per_allele_field_and_two_alleles(self):
        format_metadata = VcfMetadata.create_from_metadata_record(
            '##FORMAT=<ID=AF,Number=A,Type=Float,Description="'
            '"Allele frequency based on Flow Evaluator observation counts">')
        vcf_object = Vcf()
        vcf_object.info_and_format_metadata['FORMAT']['AF'] = format_metadata
        record = VcfRecord.create_from_record_string(
            '1\t10\tID\tT\tA,G\t10\t.\t\tAF\t2,5', self.vcf_header, vcf_object.info_and_format_metadata, 1)

        allele_record = dict()
        self.converter.add_format_columns_to_allele_record(0, allele_record, record, vcf_object)
        self.assertEqual(1, len(allele_record))
        self.assertEqual(allele_record.keys()[0], 'FORMAT.A.AF')
        self.assertEqual(allele_record.values()[0], '2')
        self.converter.add_format_columns_to_allele_record(1, allele_record, record, vcf_object)
        self.assertEqual(1, len(allele_record))
        self.assertEqual(allele_record.keys()[0], 'FORMAT.A.AF')
        self.assertEqual(allele_record.values()[0], '5')

    def test_add_info_columns_to_allele_record_with_per_variant_field_with_one_value(self):
        info_metadata = VcfMetadata.create_from_metadata_record(
            '##INFO=<ID=DP,Number=1,Type=Integer,Description="Total read depth at the locus">')
        vcf_object = Vcf()
        vcf_object.info_and_format_metadata['INFO']['DP'] = info_metadata
        record = VcfRecord.create_from_record_string(
            '1\t10\tID\tT\tA\t10\t.\tDP=2\t\t', self.vcf_header, vcf_object.info_and_format_metadata, 1)

        allele_record = dict()
        self.converter.add_info_columns_to_allele_record(0, allele_record, -1, record, vcf_object)
        self.assertEqual(3, len(allele_record))
        self.assertDictEqual(allele_record, {'ID': 'ID', 'INFO.1.DP': '2', 'FUNCS': []})

    def test_add_info_columns_to_allele_record_with_per_variant_field_with_two_values(self):
        info_metadata = VcfMetadata.create_from_metadata_record(
            '##INFO=<ID=MEINFO,Number=4,Type=String,Description="Mobile element info of the form NAME,START,END,POLARITY">')
        vcf_object = Vcf()
        vcf_object.info_and_format_metadata['INFO']['MEINFO'] = info_metadata
        record = VcfRecord.create_from_record_string(
            '1\t10\tID\tT\tA\t10\t.\tMEINFO=1,2,3,4\t\t', self.vcf_header, vcf_object.info_and_format_metadata, 1)

        allele_record = dict()
        self.converter.add_info_columns_to_allele_record(0, allele_record, -1, record, vcf_object)
        self.assertEqual(3, len(allele_record))
        self.assertDictEqual(allele_record, {'ID': 'ID', 'INFO.4.MEINFO': '1,2,3,4', 'FUNCS': []})

    def test_add_info_columns_to_allele_record_with_per_allele_field_with_one_allele(self):
        info_metadata = VcfMetadata.create_from_metadata_record(
            '##INFO=<ID=AF,Number=A,Type=Float,Description="Allele frequency based on Flow Evaluator observation counts">')
        vcf_object = Vcf()
        vcf_object.info_and_format_metadata['INFO']['AF'] = info_metadata
        record = VcfRecord.create_from_record_string(
            '1\t10\tID\tT\tA\t10\t.\tAF=1\t\t', self.vcf_header, vcf_object.info_and_format_metadata, 1)

        allele_record = dict()
        self.converter.add_info_columns_to_allele_record(0, allele_record, -1, record, vcf_object)
        self.assertEqual(3, len(allele_record))
        self.assertDictEqual(allele_record, {'ID': 'ID', 'INFO.A.AF': '1', 'FUNCS': []})

    def test_add_info_columns_to_allele_record_with_per_allele_field_with_two_alleles(self):
        info_metadata = VcfMetadata.create_from_metadata_record(
            '##INFO=<ID=AF,Number=A,Type=Float,Description="Allele frequency based on Flow Evaluator observation counts">')
        vcf_object = Vcf()
        vcf_object.info_and_format_metadata['INFO']['AF'] = info_metadata
        record = VcfRecord.create_from_record_string(
            '1\t10\tID\tT\tA,G\t10\t.\tAF=1,2\t\t', self.vcf_header, vcf_object.info_and_format_metadata, 1)

        allele_record = dict()
        self.converter.add_info_columns_to_allele_record(0, allele_record, -1, record, vcf_object)
        self.assertEqual(3, len(allele_record))
        self.assertDictEqual(allele_record, {'ID': 'ID', 'INFO.A.AF': '1', 'FUNCS': []})
        self.converter.add_info_columns_to_allele_record(1, allele_record, -1, record, vcf_object)
        self.assertEqual(3, len(allele_record))
        self.assertDictEqual(allele_record, {'ID': 'ID', 'INFO.A.AF': '2', 'FUNCS': []})

    def test_add_info_columns_to_allele_record_with_oid(self):
        info_metadata = VcfMetadata.create_from_metadata_record(
            '##INFO=<ID=OID,Number=.,Type=String,Description="List of original Hotspot IDs">')
        vcf_object = Vcf()
        vcf_object.info_and_format_metadata['INFO']['OID'] = info_metadata
        record = VcfRecord.create_from_record_string(
            '1\t10\tID\tT\tA,G\t10\t.\tOID=1,2\t\t', self.vcf_header, vcf_object.info_and_format_metadata, 1)

        allele_record = dict()
        self.converter.add_info_columns_to_allele_record(0, allele_record, 1, record, vcf_object)
        self.assertEqual(3, len(allele_record))
        self.assertDictEqual(allele_record, {'ID': '2', 'INFO...OID': '2', 'FUNCS': []})

    def test_add_info_columns_to_allele_record_with_general_o_indexed_field(self):
        info_metadata = VcfMetadata.create_from_metadata_record(
            '##INFO=<ID=OMAPALT,Number=.,Type=String,Description="Maps OID,OPOS,OREF,OALT entries to specific ALT alleles">')
        vcf_object = Vcf()
        vcf_object.info_and_format_metadata['INFO']['OMAPALT'] = info_metadata
        record = VcfRecord.create_from_record_string(
            '1\t10\tID\tT\tA,G\t10\t.\tOMAPALT=1,2\t\t', self.vcf_header, vcf_object.info_and_format_metadata, 1)

        allele_record = dict()
        self.converter.add_info_columns_to_allele_record(0, allele_record, 1, record, vcf_object)
        self.assertEqual(3, len(allele_record))
        self.assertDictEqual(allele_record, {'ID': 'ID', 'INFO...OMAPALT': '2', 'FUNCS': []})

    def test_handle_func_when_func_is_positional(self):
        allele_record = dict({'FUNCS': []})
        func = VcfFuncBlock.create_from_func_string("[{'gene': 'EGFR'}]")[0]
        self.converter.gene_whitelist = ['EGFR']
        self.converter.handle_functional_annotation(func, allele_record, dict({}))
        self.assertEqual(1, len(allele_record))
        self.assertEqual(allele_record.keys()[0], 'FUNCS')
        self.assertEqual(1, len(allele_record['FUNCS']))
        self.assertDictEqual(allele_record['FUNCS'][0], func)

    def test_handle_func_when_func_is_per_allele_and_matches(self):
        func_string = "[{'gene': 'EGFR','normalizedRef':'T','normalizedAlt':'G','normalizedPos':'10'}]"
        allele_record = dict({'FUNCS': []})
        func = VcfFuncBlock.create_from_func_string(func_string)[0]
        self.converter.gene_whitelist = ['EGFR']
        self.converter.handle_functional_annotation(func, allele_record, dict({'REF': 'T', 'ALT': 'G', 'POS': 10}))
        self.assertEqual(1, len(allele_record))
        self.assertEqual(allele_record.keys()[0], 'FUNCS')
        self.assertEqual(1, len(allele_record['FUNCS']))
        self.assertDictEqual(allele_record['FUNCS'][0], func)

    def test_handle_func_when_func_is_per_allele_and_does_not_match(self):
        func_string = "[{'gene': 'EGFR','normalizedRef':'T','normalizedAlt':'A','normalizedPos':'10'}]"
        allele_record = dict({'FUNCS': []})
        func = VcfFuncBlock.create_from_func_string(func_string)[0]
        self.converter.handle_functional_annotation(func, allele_record, dict({'REF': 'T', 'ALT': 'G', 'POS': 10}))
        self.assertEqual(1, len(allele_record))
        self.assertEqual(allele_record.keys()[0], 'FUNCS')
        self.assertEqual(1, len(allele_record['FUNCS']))

    def test_handle_func_when_func_does_not_contain_whitelisted_gene(self):
        func_string = "[{'gene': 'EGFR','normalizedRef':'T','normalizedAlt':'A','normalizedPos':'10'}]"
        allele_record = dict({'FUNCS': []})
        func = VcfFuncBlock.create_from_func_string(func_string)[0]
        self.converter.gene_whitelist = ['KRAS']
        self.converter.handle_functional_annotation(func, allele_record, dict({'REF': 'T', 'ALT': 'A', 'POS': 10}))
        self.assertEqual(1, len(allele_record))
        self.assertEqual(allele_record.keys()[0], 'FUNCS')
        self.assertEqual(1, len(allele_record['FUNCS']))

    def test_handle_func_when_func_contains_whitelisted_gene(self):
        func_string = "[{'gene': 'EGFR','normalizedRef':'T','normalizedAlt':'A','normalizedPos':'10'}]"
        allele_record = dict({'FUNCS': []})
        func = VcfFuncBlock.create_from_func_string(func_string)[0]
        self.converter.gene_whitelist = ['EGFR']
        self.converter.handle_functional_annotation(func, allele_record, dict({'REF': 'T', 'ALT': 'A', 'POS': 10}))
        self.assertEqual(1, len(allele_record))
        self.assertEqual(allele_record.keys()[0], 'FUNCS')
        self.assertEqual(1, len(allele_record['FUNCS']))
        self.assertEqual(allele_record['FUNCS'][0], func)

    def test_handle_func_when_keep_all_genes_is_true(self):
        func_string = "[{'gene': 'EGFR','normalizedRef':'T','normalizedAlt':'A','normalizedPos':'10'}]"
        allele_record = dict({'FUNCS': []})
        func = VcfFuncBlock.create_from_func_string(func_string)[0]
        self.converter.keep_all_genes = True
        self.converter.gene_whitelist = ['TANK']
        self.converter.handle_functional_annotation(func, allele_record, dict({'REF': 'T', 'ALT': 'A', 'POS': 10}))
        self.assertEqual(1, len(allele_record))
        self.assertEqual(allele_record.keys()[0], 'FUNCS')
        self.assertEqual(1, len(allele_record['FUNCS']))
        self.assertEqual(allele_record['FUNCS'][0], func)

    def test_calculate_consolidated_fields_with_empty_column_list(self):
        self.assertSetEqual(self.converter.calculate_consolidated_fields([{'foo': 3}, {'bar': 5}]), {'foo', 'bar'})

    def test_calculate_consolidated_fields_with_column_list(self):
        self.assertEqual(self.converter.calculate_consolidated_fields([{'foo': 3}, {'bar': 5}], ['foo']), {'foo'})

    def test_sort_header_fields_with_limited_field_set(self):
        self.assertEqual(self.converter.sort_header_fields(['rowtype', 'vcf.rownum']), ['vcf.rownum', 'rowtype'])

    def test_sort_header_fields_with_basic_field_set(self):
        fields = [
            'vcf.rownum', 'rowtype', 'call', 'ID.count', 'ALT.count', 'OID.count', 'FUNC.count', 'ALT.idx', 'OID.idx',
            'CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER'
        ]
        sorted_fields = self.converter.sort_header_fields(fields[::-1])
        self.assertEqual(sorted_fields, fields)

    def test_sort_header_fields_with_info_fields(self):
        fields = [
            'INFO.0.HS', 'INFO.1.RAW_CN', 'INFO.4.MEINFO', 'INFO...FR', 'INFO.A.LEN'
        ]
        self.assertEqual(self.converter.sort_header_fields(fields[::-1]),
                         ['INFO...FR', 'INFO.0.HS', 'INFO.1.RAW_CN', 'INFO.4.MEINFO', 'INFO.A.LEN'])

    def test_sort_header_fields_with_format_fields(self):
        fields = [
            'FORMAT.1.GQ', 'FORMAT.1.DP', 'FORMAT.A.AF', 'FORMAT.A.SAR'
        ]
        self.assertEqual(self.converter.sort_header_fields(fields[::-1]),
                         ['FORMAT.1.DP', 'FORMAT.1.GQ', 'FORMAT.A.AF', 'FORMAT.A.SAR'])

    def test_sort_header_fields_with_func_fields(self):
        fields = [
            'FUNC0.exon', 'FUNC2.transcript', 'FUNC3.location', 'FUNC1.gene', 'FUNC1.proteinPos'
        ]
        self.assertEqual(self.converter.sort_header_fields(fields[::-1]),
                         ['FUNC0.exon', 'FUNC1.gene', 'FUNC1.proteinPos', 'FUNC2.transcript', 'FUNC3.location'])

    def test_sort_header_fields_with_mixed_fields(self):
        fields = [
            'FUNC0.exon', 'vcf.rownum', 'FUNC2.transcript', 'FORMAT.1.GQ', 'FUNC1.gene', 'INFO.4.MEINFO'
        ]
        self.assertEqual(self.converter.sort_header_fields(fields[::-1]),
                         ['vcf.rownum', 'INFO.4.MEINFO', 'FORMAT.1.GQ', 'FUNC0.exon', 'FUNC1.gene', 'FUNC2.transcript'])

    def test_pivot_functional_annotations_with_two_funcs(self):
        allele_record = {'FUNCS': [{'foo': 'bar'}, {'baz': 'quux'}]}
        self.converter.pivot_functional_annotations(allele_record)
        self.assertDictEqual(allele_record, {'FUNC1.foo': 'bar', 'FUNC2.baz': 'quux'})

    def test_pivot_function_annotations_with_list_value(self):
        allele_record = {'FUNCS': [{'foo': ['bar', 'baz']}]}
        self.converter.pivot_functional_annotations(allele_record)
        self.assertDictEqual(allele_record, {'FUNC1.foo': ['bar', 'baz']})

    def test_determine_call_status_for_record_when_cnv_amp(self):
        allele_record = {'INFO.1.SVTYPE': 'CNV', 'INFO...CI': '0.05:5,0.95:2'}
        self.converter.determine_call_status_for_record(allele_record)
        self.assertEqual('AMP', allele_record['call'])

    def test_determine_call_status_for_record_when_cnv_del(self):
        allele_record = {'INFO.1.SVTYPE': 'CNV', 'INFO...CI': '0.05:2,0.95:.5'}
        self.converter.determine_call_status_for_record(allele_record)
        self.assertEqual('DEL', allele_record['call'])

    def test_determine_call_status_for_record_when_cnv_neither_amp_nor_del(self):
        allele_record = {'INFO.1.SVTYPE': 'CNV', 'INFO...CI': '0.05:2,0.95:3'}
        self.converter.determine_call_status_for_record(allele_record)
        self.assertEqual('NEG', allele_record['call'])

    def test_determine_call_status_for_record_when_fusion_positive(self):
        allele_record = {'INFO.1.SVTYPE': 'Fusion', 'FILTER': 'PASS'}
        self.converter.determine_call_status_for_record(allele_record)
        self.assertEqual('POS', allele_record['call'])

    def test_determine_call_status_for_record_when_fusion_negative(self):
        allele_record = {'INFO.1.SVTYPE': 'Fusion', 'FILTER': '.'}
        self.converter.determine_call_status_for_record(allele_record)
        self.assertEqual('NEG', allele_record['call'])

    def test_determine_call_status_for_record_when_mutation_nocall(self):
        allele_record = {'FORMAT.1.GT': './.'}
        self.converter.determine_call_status_for_record(allele_record)
        self.assertEqual('NOCALL', allele_record['call'])

    def test_determine_call_status_for_record_when_mutation_positive(self):
        allele_record = {'FORMAT.1.GT': '1/2', 'ALT.idx': '1'}
        self.converter.determine_call_status_for_record(allele_record)
        self.assertEqual('POS', allele_record['call'])

    def test_determine_call_status_for_record_when_mutation_negative(self):
        allele_record = {'FORMAT.1.GT': '2/2', 'ALT.idx': '1'}
        self.converter.determine_call_status_for_record(allele_record)
        self.assertEqual('NEG', allele_record['call'])

    def test_determine_rowtype_for_record_when_type_present(self):
        allele_record = {'INFO.A.TYPE': 'foo', 'INFO.1.SVTYPE': 'bar'}
        self.converter.determine_rowtype_for_record(allele_record)
        self.assertEqual('foo', allele_record['rowtype'])

    def test_determine_rowtype_for_record_when_type_not_present(self):
        allele_record = {'INFO.1.SVTYPE': 'bar'}
        self.converter.determine_rowtype_for_record(allele_record)
        self.assertEqual('bar', allele_record['rowtype'])

    class MockFile:
        def __init__(self):
            self.lines = []

        def write(self, line):
            self.lines.append(line)

    def test_write_metadata(self):
        output_file = self.MockFile()
        self.converter.write_metadata(output_file, ['##a=1', '##b=2', '##c=3'], ['b', 'a'])
        self.assertEqual(['##b=2\n', '##a=1\n'], output_file.lines)

    def test_write_metadata_when_hashtag_included(self):
        output_file = self.MockFile()
        self.converter.write_metadata(output_file, ['##a=1', '##b=2', '##c=3'], ['##b', '##a'])
        self.assertEqual(['##b=2\n', '##a=1\n'], output_file.lines)

    def test_write_metadata_when_case_different(self):
        output_file = self.MockFile()
        self.converter.write_metadata(output_file, ['##a=1', '##b=2', '##c=3'], ['C'])
        self.assertEqual(['##c=3\n'], output_file.lines)

    def test_write_metadata_when_no_fields_specified(self):
        output_file = self.MockFile()
        self.converter.write_metadata(output_file, ['##a=1', '##b=2', '##c=3', '##sampleGender=M'], [])
        self.assertEqual([], output_file.lines)

    def test_write_metadata_when_duplicate_metadata_fields(self):
        output_file = self.MockFile()
        self.converter.write_metadata(output_file, ['##a=1', '##a=2', '##b=2', '##c=3'], ['a', 'c'])
        self.assertEqual(['##a=1\n', '##a=2\n', '##c=3\n'], output_file.lines)

    def test_write_metadata_default_meta_fields(self):
        output_file = self.MockFile()
        metadata = ['##A=1',
                    '##sampleGender=M',
                    '##sampleDiseaseType=Melanoma',
                    '##CellularityAsAFractionBetween0-1=0.5',
                    '##B=1',
                    '##TotalMappedFusionPanelReads=1',
                    '##mapd=1',
                    '##C=3']
        self.converter.write_metadata(output_file, metadata, None)

        expected = ['##sampleGender=M\n',
                    '##sampleDiseaseType=Melanoma\n',
                    '##CellularityAsAFractionBetween0-1=0.5\n',
                    '##TotalMappedFusionPanelReads=1\n',
                    '##mapd=1\n']
        self.assertEqual(expected, output_file.lines)