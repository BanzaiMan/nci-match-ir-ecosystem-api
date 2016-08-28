import os
import re
import sys
import csv
from collections import OrderedDict


class AlleleToOriginalMapper(object):
    def __init__(self):
        self.allele_to_original_map = dict()

    @classmethod
    def create_from_allele_lists(cls, alleles, original_alleles):
        return_obj = cls()
        return_obj.generate_allele_to_original_map(alleles, original_alleles)
        return return_obj

    def generate_allele_to_original_map(self, alleles, original_alleles):
        for allele_index, allele in enumerate(alleles):
            self.allele_to_original_map[allele_index] = []
            for orig_allele_index, orig_allele in enumerate(original_alleles):
                if allele == orig_allele:
                    self.allele_to_original_map[allele_index].append(orig_allele_index)

    def __getitem__(self, item):
        return self.allele_to_original_map[item]


class VcfConverter(object):
    GENE_WHITELIST_FILE_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'oncomine_genes.txt')
    DEFAULT_META_FIELDS = ['sampleGender',
                           'sampleDiseaseType',
                           'CellularityAsAFractionBetween0-1',
                           'TotalMappedFusionPanelReads',
                           'mapd']

    def __init__(self):
        self.keep_all_genes = False
        self.gene_whitelist = []

    @staticmethod
    def normalized_info_matches(func, normalized_variant_info):
        norm_ref = normalized_variant_info.get('REF')
        norm_alt = normalized_variant_info.get('ALT')
        norm_pos = normalized_variant_info.get('POS')
        func_ref = func.get('normalizedRef')
        func_alt = func.get('normalizedAlt')
        func_pos = func.get('normalizedPos')
        return all([func_ref is None, func_alt is None, func_pos is None]) \
            or all([norm_ref == func_ref, norm_alt == func_alt, norm_pos == func_pos])

    @staticmethod
    def one_is_superset_of_two(one, two):
        return all(item in one.items() for item in two.items()) and one != two

    @staticmethod
    def position_information(func):
        return OrderedDict({
            prop: value for prop, value in func.items() if prop in ['gene', 'transcript', 'location', 'exon']
        })

    def update_existing_func(self, allele_funcs, func, func_position_information, normalized_variant_info):
        func_was_updated = False
        for func_index, existing_func in enumerate(allele_funcs):
            if self.normalized_info_matches(func, normalized_variant_info):
                if self.one_is_superset_of_two(func, existing_func):
                    allele_funcs[func_index] = func
                    func_was_updated = True
                elif self.one_is_superset_of_two(existing_func, func):
                    func_was_updated = True
            elif self.one_is_superset_of_two(func_position_information, existing_func):
                allele_funcs[func_index] = func_position_information
                func_was_updated = True
            elif self.one_is_superset_of_two(existing_func, func_position_information):
                func_was_updated = True
        return func_was_updated

    def add_func(self, allele_funcs, func, func_position_information, normalized_variant_info):
        if self.normalized_info_matches(func, normalized_variant_info):
            self.insert_func(func, allele_funcs)
        else:
            self.insert_func(func_position_information, allele_funcs)

    def insert_func(self, func, funcs):
        if func['gene'] in self.gene_whitelist:
            funcs.insert(0, func)
        else:
            funcs.append(func)

    def handle_functional_annotation(self, func, allele_record, normalized_variant_info):
        func_position_information = self.position_information(func)
        allele_funcs = allele_record['FUNCS']

        if len(allele_funcs) == 0:
            self.add_func(allele_funcs, func, func_position_information, normalized_variant_info)
        else:
            did_update = self.update_existing_func(
                allele_funcs, func, func_position_information, normalized_variant_info)

            if not did_update:
                self.add_func(allele_funcs, func, func_position_information, normalized_variant_info)

    def add_info_columns_to_allele_record(self, allele_index, allele_record, o_index, record, vcf_object):
        info_key = 'INFO'
        allele_record['FUNCS'] = []
        allele_record['ID'] = record['ID'][0]
        for info_property in record[info_key]:
            info_property_column_name = self.get_output_column_name('INFO', vcf_object, info_property)
            if info_property == 'FUNC':
                for func in record['INFO']['FUNC']:
                    if self.keep_all_genes or func['gene'] in self.gene_whitelist:
                        if record.record_type == 'Mutation':
                            self.handle_functional_annotation(
                                func, allele_record, record.normalized_variant_information[allele_index])
                        else:
                            self.handle_functional_annotation(func, allele_record, {})
            else:
                if record[info_key].is_per_allele(info_property):
                    allele_record[info_property_column_name] = record[info_key][info_property][allele_index]
                elif record[info_key].is_o_indexed(info_property):
                    allele_record[info_property_column_name] = record[info_key][info_property][o_index]
                    if info_property == 'OID':
                        allele_record['ID'] = record[info_key][info_property][o_index]
                else:
                    if type(record[info_key][info_property]) is list:
                        allele_record[info_property_column_name] = ','.join(record[info_key][info_property])
                    else:
                        allele_record[info_property_column_name] = record[info_key][info_property]

    def add_format_columns_to_allele_record(self, allele_index, allele_record, record, vcf_object):
        format_key = 'GENOTYPE'
        for format_property in record[format_key]:
            format_property_column_name = self.get_output_column_name('FORMAT', vcf_object, format_property)

            if record[format_key].is_per_allele(format_property):
                allele_record[format_property_column_name] = record[format_key][format_property][allele_index]
            else:
                if type(record[format_key][format_property]) is list:
                    allele_record[format_property_column_name] = ','.join(record[format_key][format_property])
                else:
                    allele_record[format_property_column_name] = record[format_key][format_property]

    @staticmethod
    def get_output_column_name(metadata_type, vcf_object, metadata_property):
            metadata_object = vcf_object.info_and_format_metadata[metadata_type][metadata_property]
            return '{metadata_type}.{num}.{id}'.format(
                metadata_type=metadata_type, num=metadata_object['Number'], id=metadata_object['ID'])

    @staticmethod
    def determine_rowtype_for_record(record):
        record['rowtype'] = record['INFO.A.TYPE'] if record.get('INFO.A.TYPE') else record['INFO.1.SVTYPE']

    @staticmethod
    def determine_call_status_for_record(record):
        call = None
        record_svtype_column = 'INFO.1.SVTYPE'
        gt_column_name = 'FORMAT.1.GT'
        if record.get(record_svtype_column):
            if record[record_svtype_column] == 'CNV':
                ci_values = dict(ci_thresholds.split(':') for ci_thresholds in record['INFO...CI'].split(','))
                is_amp = False
                is_del = False
                call = 'NEG'

                if float(ci_values['0.05']) >= 4:
                    is_amp = True
                    call = 'AMP'

                if float(ci_values['0.95']) <= 1:
                    is_del = True
                    call = 'DEL'

                if is_amp and is_del:
                    call = 'NEG'
                    sys.stderr.write('WARNING: VCF record {record} was called as both an AMP and a DEL based on its '
                                     'confidence interval values: 5%: {oh_five}, 95%: {nine_five}.'.format(
                                         record=record['vcf.rownum'], oh_five=ci_values['0.05'],
                                         nine_five=ci_values['0.95']
                                     ))
            else:
                if record['FILTER'] == 'PASS':
                    call = 'POS'
                else:
                    call = 'NEG'
        else:
            if record.get(gt_column_name):
                if record[gt_column_name] == './.':
                    call = 'NOCALL'
                else:
                    alt_index = record[gt_column_name].split('/')
                    call = 'POS' if str(record['ALT.idx']) in alt_index else 'NEG'
        record['call'] = call

    def read_gene_whitelist(self):
        with open(self.GENE_WHITELIST_FILE_NAME, 'r') as gene_whitelist_file:
            for gene in gene_whitelist_file:
                self.gene_whitelist.append(gene.rstrip('\r\n'))

    @staticmethod
    def add_calculated_fields_to_record(allele_record, data_record_index, allele, allele_index, record, o_index):
        allele_record['vcf.rownum'] = data_record_index
        allele_record['ALT'] = allele
        allele_record['ALT.idx'] = allele_index + 1
        allele_record['ALT.count'] = len(record['ALT'])
        allele_record['ID.count'] = len(record['ID'])
        allele_record['OID.idx'] = (1 + o_index) if o_index is not None else ''
        allele_record['OID.count'] = len(record['INFO']['OID']) if 'OID' in record['INFO'] else ''
        allele_record['FUNC.count'] = len(record['INFO']['FUNC']) if 'FUNC' in record['INFO'] else 0

    def convert(self, vcf_object, keep_all_genes=False, keep_all_cnvs=False):
        print 'Converting \'{vcf}\'...'.format(vcf=vcf_object.file_name)
        data_record_start_line_number = vcf_object.total_header_length + 1
        all_allele_records = []
        self.keep_all_genes = keep_all_genes
        self.read_gene_whitelist()
        for record_index, record in enumerate(vcf_object.sample_data):
            allele_to_orig_mapper = None

            if not keep_all_cnvs and record.record_type == 'CNV' and len(record['ID']) == 1 and record['ID'][0] == '.':
                continue

            if record.record_type == 'Mutation':
                allele_to_orig_mapper = AlleleToOriginalMapper.create_from_allele_lists(
                    record['ALT'], record['INFO']['OMAPALT'])

            for allele_index, allele in enumerate(record['ALT']):
                o_indices = [None]
                if record.record_type == 'Mutation':
                    o_indices = allele_to_orig_mapper[allele_index]
                for o_index in o_indices:
                    allele_record = dict()

                    for column in ['CHROM', 'POS', 'REF', 'FILTER', 'QUAL']:
                        allele_record[column] = record[column]

                    self.add_calculated_fields_to_record(
                        allele_record, data_record_start_line_number + record_index,
                        allele, allele_index, record, o_index)

                    self.add_info_columns_to_allele_record(
                        allele_index, allele_record, o_index, record, vcf_object)
                    if record.record_type in ['CNV', 'Mutation']:
                        self.add_format_columns_to_allele_record(allele_index, allele_record, record, vcf_object)
                    self.pivot_functional_annotations(allele_record)
                    self.determine_call_status_for_record(allele_record)
                    self.determine_rowtype_for_record(allele_record)

                    all_allele_records.append(allele_record)
        return all_allele_records

    def write_to_file(self, output_file_name, all_allele_records, metadata, meta_fields, column_list=list()):
        print 'Writing to \'{tsv}\'...'.format(tsv=output_file_name)
        output_dir = os.path.dirname(output_file_name)
        if output_dir != '' and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open(output_file_name, 'w') as output_file:
            self.write_metadata(output_file, metadata, meta_fields)

            csvwriter = csv.writer(output_file, delimiter='\t',
                                   quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\n')
            all_fields = self.sort_header_fields(self.calculate_consolidated_fields(all_allele_records, column_list))
            csvwriter.writerow([field for field in all_fields])
            for record in all_allele_records:
                record_builder = []
                for field in all_fields:
                    if re.match('(FORMAT|INFO)\.0\.*', field):
                        if field in record:
                            record_builder.append('True')
                        else:
                            record_builder.append('False')
                    elif record.get(field) is not None and type(record[field]) is list:
                        record_builder.append(','.join([str(item) for item in record[field]]))
                    elif record.get(field) is not None:
                        record_builder.append(str(record[field]))
                    else:
                        record_builder.append('')
                csvwriter.writerow(record_builder)

    def write_metadata(self, output_file, metadata, meta_fields):
        for field in (meta_fields if meta_fields is not None else self.DEFAULT_META_FIELDS):
            [output_file.write(line + '\n') for line in metadata
             if line.split('=')[0].lstrip('#').lower() == field.lstrip('#').lower()]

    @staticmethod
    def sort_header_fields(header_fields):
        sorted_fields = [item for item in [
            'vcf.rownum', 'rowtype', 'call', 'ID.count', 'ALT.count', 'OID.count', 'FUNC.count', 'ALT.idx', 'OID.idx',
            'CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER'
        ] if item in header_fields]
        sorted_fields.extend(sorted([field for field in header_fields if field.startswith('INFO')]))
        sorted_fields.extend(sorted([field for field in header_fields if field.startswith('FORMAT')]))
        sorted_fields.extend(sorted([field for field in header_fields
                                     if field.startswith('FUNC') and field != 'FUNC.count']))
        return sorted_fields

    @staticmethod
    def pivot_functional_annotations(allele_record):
        for func_index, func in enumerate(allele_record['FUNCS'], 1):
            for func_property, func_value in func.items():
                func_property_column_name = 'FUNC{index}.{prop}'.format(index=func_index, prop=func_property)
                allele_record[func_property_column_name] = func_value
        del allele_record['FUNCS']

    @staticmethod
    def calculate_consolidated_fields(all_allele_records, column_list=list()):
        all_fields = set()
        for record in all_allele_records:
            all_fields.update([field for field in record])

        if len(column_list) > 0:
            all_fields = set([field for field in all_fields if field in column_list])
            all_fields.update([field for field in all_fields if field.startswith('FUNC') and 'FUNC' in column_list])

        return all_fields
