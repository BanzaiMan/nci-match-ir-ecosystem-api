import os
import re
import sys
import json
from collections import OrderedDict

class IonVcf(object):
    NORMALIZED_ALT_FIELD_NAME = 'normalizedAlt'
    NORMALIZED_REF_FIELD_NAME = 'normalizedRef'
    NORMALIZED_POS_FIELD_NAME = 'normalizedPos'

    def __init__(self):
        self.file_name = None
        self.metadata_raw = []
        self.sample_run_metadata = []
        self.info_and_format_metadata = dict({'INFO': OrderedDict(), 'FORMAT': OrderedDict()})
        self.info_and_format_metadata_length = 0
        self.header = OrderedDict()
        self.sample_data = []
        self.ir_vcf_version = None

    @classmethod
    def create_from_vcf_file(cls, vcf_file_name):
        return_object = cls()
        return_object.read_from_vcf_file(vcf_file_name)
        return return_object

    @classmethod
    def create_from_lines(cls, lines):
        return_object = cls()
        return_object.read_from_lines(lines)
        return return_object

    @property
    def total_header_length(self):
        column_header_length = 1
        return len(self.sample_run_metadata) + self.info_and_format_metadata_length + column_header_length

    def read_from_vcf_file(self, vcf_file_name):
        self.file_name = vcf_file_name
        if not os.path.isfile(vcf_file_name):
            sys.exit('The VCF file \'{vcf}\' does not exist!'.format(vcf=vcf_file_name))
        with open(vcf_file_name, 'r') as vcf_file:
            lines = vcf_file.readlines()
            self.read_from_lines(lines)

    def read_from_lines(self, lines):
        for (row_index, line) in enumerate(lines):
            line = line.rstrip('\r\n')
            if line.startswith('##'):
                self.metadata_raw.append(line)
                if line.startswith('##INFO') or line.startswith('##FORMAT'):
                    metadata_object = VcfMetadata.create_from_metadata_record(line)
                    self.info_and_format_metadata[metadata_object.metadata_type][metadata_object['ID']] \
                        = metadata_object
                    self.info_and_format_metadata_length += 1
                elif line.startswith('##IonReporterExportVersion='):
                    ir_export_version_parts = line.split('=')
                    self.ir_vcf_version = ir_export_version_parts[1]
                    self.sample_run_metadata.append(line)
                else:
                    self.sample_run_metadata.append(line)
            elif line.startswith('#'):
                columns = line.replace('#', '', 1).split('\t')
                for index, column in enumerate(columns):
                    self.header[column] = index
            elif len(line) > 0:
                self.sample_data.append(VcfRecord.create_from_record_string(
                    line, self.header, self.info_and_format_metadata, row_index))

        info_properties_without_metadata = set()
        for record in self.sample_data:
            info_properties_without_metadata.update(record['INFO'].info_properties_without_metadata)

        if len(info_properties_without_metadata) > 0:
            print 'Warning - the following INFO properties do not have associated metadata entries, ' \
                'and will be treated as nonallele-specific: ', \
                ','.join(sorted(info_properties_without_metadata))

    def write_to_file(self, file_name):
        if file_name.endswith('.vcf'):
            self.write_to_vcf_file(file_name)

    def write_to_vcf_file(self, file_name):
        if not os.path.isfile(file_name):
            with open(file_name, 'w') as vcf_file:
                vcf_file.write(str(self))
        else:
            raise IOError('File \'{file}\' already exists!'.format(file=file_name))

    def __str__(self):
        vcf_strs = []
        [vcf_strs.append(str(record)) for record in self.sample_run_metadata]
        for metadata_key, metadata_obj in self.info_and_format_metadata['INFO'].items():
            vcf_strs.append(str(metadata_obj))
        for metadata_key, metadata_obj in self.info_and_format_metadata['FORMAT'].items():
            vcf_strs.append(str(metadata_obj))
        vcf_strs.append('#' + '\t'.join([field_name for field_name in self.header]))
        [vcf_strs.append(str(record)) for record in self.sample_data]
        return '\n'.join(vcf_strs)

class VcfInfoField(object):
    OFIELDS = ['OID', 'OMAPALT', 'OPOS', 'OREF', 'OALT']

    def __init__(self):
        self.properties = OrderedDict()
        self.metadata = None
        self.info_properties_without_metadata = []

    @classmethod
    def create_from_info_string(cls, info_string, info_metadata):
        return_object = cls()
        return_object.metadata = info_metadata
        return_object.set_from_info_string(info_string)
        return return_object

    def set_from_info_string(self, info_string):
        parts = info_string.split(';')
        for part in parts:
            if part:
                if '=' in part:
                    key, value = part.split('=', 1)
                else:
                    key, value = part, None

                if key == 'FUNC':
                    value = VcfFuncBlock.create_from_func_string(value)
                elif self.is_per_allele(key) or self.is_o_indexed(key):
                    value = value.split(',')

                self.properties[key] = value

    def is_per_allele(self, info_property):
        if info_property not in self.metadata:
            self.info_properties_without_metadata.append(info_property)
            return False

        return self.metadata[info_property].is_per_allele()

    def is_o_indexed(self, info_property):
        return info_property in self.OFIELDS

    def __eq__(self, other):
        return type(other) == type(self) and other.properties == self.properties

    def __ne__(self, other):
        return not self == other

    def __getitem__(self, item):
        return self.properties[item]

    def __iter__(self):
        return iter(self.properties)

    def __str__(self):
        property_strs = []
        for info_prop, info_value in self.properties.items():
            if info_prop != 'FUNC' and self.is_per_allele(info_prop) or self.is_o_indexed(info_prop):
                value_str = ','.join([item for item in info_value])
            elif info_value is not None:
                value_str = str(info_value)
            else:
                value_str = None
            property_string = info_prop
            if value_str:
                property_string += '={value}'.format(value=value_str)
            property_strs.append(property_string)
        return ';'.join(property_strs)

class VcfFuncBlock(object):
    def __init__(self):
        self.funcs = []

    @classmethod
    def create_from_func_string(cls, func_string):
        return_object = cls()
        return_object.set_from_func_string(func_string)
        return return_object

    def set_from_func_string(self, func_string):
        decoder = json.JSONDecoder(object_pairs_hook=OrderedDict)
        self.funcs = decoder.decode(func_string.replace('\'', '"'))
        for func in self.funcs:
            for key, value in func.items():
                if type(value) in [str, unicode]:
                    try:
                        func[key] = int(value)
                    except ValueError:
                        try:
                            func[key] = float(value)
                        except ValueError:
                            pass

    def __eq__(self, other):
        return type(other) == type(self) and other.funcs == self.funcs

    def __ne__(self, other):
        return not self == other

    def __getitem__(self, item):
        return self.funcs[item]

    def __len__(self):
        return len(self.funcs)

    def __str__(self):
        func_strs = []
        for func in self.funcs:
            func_str = ','.join(['\'{key}\':\'{val}\''.format(key=key, val=value) for key, value in func.items()])
            func_strs.append('{' + func_str + '}')
        return '[' + ','.join(func_strs) + ']'

class VcfGenotypeInformation(object):
    def __init__(self):
        self.properties = dict()
        self.metadata = None

    @classmethod
    def create_from_genotype_information(cls, format_string, genotype_information_string, format_metadata):
        return_object = cls()
        return_object.metadata = format_metadata
        return_object.set_from_genotype_information(format_string, genotype_information_string)
        return return_object

    def set_from_genotype_information(self, format_string, genotype_information_string):
        gt_properties = format_string.split(':')
        gt_values = genotype_information_string.split(':')
        for index, value in enumerate(gt_values):
            gt_values[index] = value.split(',')
        self.properties = OrderedDict(zip(gt_properties, gt_values))

    def as_format_string(self):
        return ':'.join([key for key in self.properties])

    def as_genotype_info_string(self):
        value_strings = []
        for value in self.properties.values():
            if type(value) is list:
                value_str = ','.join([item for item in value])
            else:
                value_str = str(value)
            value_strings.append(value_str)
        return ':'.join(value_strings)

    def is_per_allele(self, genotype_property):
        return self.metadata[genotype_property].is_per_allele()

    def __eq__(self, other):
        return type(other) == type(self) and other.properties == self.properties

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return '\t'.join([self.as_format_string(), self.as_genotype_info_string()])

    def __getitem__(self, item):
        return self.properties[item]

    def __setitem__(self, key, value):
        self.properties[key] = value

    def __iter__(self):
        return iter(self.properties)

class VcfMetadata(object):
    METADATA_TYPE_SEARCH_PATTERN = '^##(.+?)='
    METADATA_EXTRACT_PATTERN = '##{metadata_type}=<(.+?)>'

    def __init__(self):
        self.metadata_type = None
        self.properties = dict()

    @classmethod
    def create_from_metadata_record(cls, metadata_record):
        return_object = cls()
        return_object.set_from_metadata_record(metadata_record)
        return return_object

    def set_from_metadata_record(self, metadata_record):
        self.metadata_type = re.search(self.METADATA_TYPE_SEARCH_PATTERN, metadata_record).group(1)
        metadata = re.search(self.METADATA_EXTRACT_PATTERN.format(
            metadata_type=self.metadata_type), metadata_record).group(1)

        for metadata_property in metadata.split(',', 3):
            key, value = metadata_property.split('=', 1)
            self.properties[key] = value

    def is_per_allele(self):
        return self['Number'] == 'A'

    def __getitem__(self, item):
        return self.properties[item]

    def __setitem__(self, key, value):
        self.properties[key] = value

    def __iter__(self):
        return iter(self.properties)

    def __eq__(self, other):
        return type(other) == type(self) and other.properties == self.properties

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return '##{metadata_type}=<ID={id},Number={num},Type={type},Description={desc}>'.format(
            metadata_type=self.metadata_type,
            id=self['ID'],
            num=self['Number'],
            type=self['Type'],
            desc=self['Description']
        )

class VcfRecord(object):
    def __init__(self):
        self.fields = OrderedDict()
        self.normalized_variant_information = []
        self.record_type = None
        self.row_index = None

    @classmethod
    def create_from_record_string(cls, record_string, header, info_and_format_metadata, row_index):
        return_object = cls()
        return_object.set_from_record_string(record_string, header, info_and_format_metadata, row_index)
        return return_object

    def set_from_record_string(self, record_string, header, info_and_format_metadata, row_index):
        self.fields = OrderedDict(zip(header, record_string.split('\t')))
        self.row_index = row_index

        svtype_pattern = re.compile('SVTYPE=(\w+)')

        result = svtype_pattern.search(self['INFO'])
        if result is not None:
            self.record_type = result.group(1)

        if self.record_type is None:
            self.record_type = 'Mutation'

        sample_key = self.fields.keys()[-1] if self.record_type in ['CNV', 'Mutation'] and self.fields.keys()[-1] != 'INFO' else None
        if self.record_type in ['CNV', 'Mutation'] and 'FORMAT' in self.fields:
            self['GENOTYPE'] = VcfGenotypeInformation.create_from_genotype_information(
                self['FORMAT'], self[sample_key], info_and_format_metadata['FORMAT'])

        self['ALT'] = self['ALT'].split(',')
        self['ID'] = self['ID'].split(';')
        self['POS'] = int(self['POS'])
        self['INFO'] = VcfInfoField.create_from_info_string(self['INFO'], info_and_format_metadata['INFO'])
        self.fields.pop('FORMAT', None)

        if sample_key is not None and sample_key != 'GENOTYPE':
            self.fields.pop(sample_key, None)

        if self.record_type == 'Mutation':
            self.normalize_variant_information()

    @staticmethod
    def reverse_and_trim_common_bases_from_front(ref, alt):
        position_delta = 0
        reverse_ref, reverse_alt = ref[::-1], alt[::-1]
        while len(reverse_ref) > 1 and len(reverse_alt) > 1 and reverse_ref[0] == reverse_alt[0]:
            reverse_ref, reverse_alt = reverse_ref[1:], reverse_alt[1:]
            position_delta += 1
        return reverse_ref, reverse_alt, position_delta

    @classmethod
    def normalize_variant(cls, ref, alt, pos):
        reversed_ref, reversed_alt, position_delta = cls.reverse_and_trim_common_bases_from_front(ref, alt)
        normalized_ref, normalized_alt, position_delta = cls.reverse_and_trim_common_bases_from_front(
            reversed_ref, reversed_alt)
        return {'REF': normalized_ref, 'ALT': normalized_alt, 'POS': pos + position_delta}

    def normalize_variant_information(self):
        for alt in self['ALT']:
            self.normalized_variant_information.append(self.normalize_variant(self['REF'], alt, self['POS']))

    def format_field_value_for_printing(self, field_name):
        if field_name in ['ID']:
            return ';'.join(self[field_name])
        elif field_name in ['ALT']:
            return ','.join(self[field_name])
        else:
            return str(self[field_name])

    def __getitem__(self, item):
        return self.fields[item]

    def __setitem__(self, key, value):
        self.fields[key] = value

    def __delitem__(self, key):
        del self.fields[key]

    def __iter__(self):
        return iter(self.fields)

    def __str__(self):
        return '\t'.join([self.format_field_value_for_printing(field) for field in self])
