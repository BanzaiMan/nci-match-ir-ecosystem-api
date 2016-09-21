#!/usr/bin/env python

import os
import sys
import argparse
import textwrap
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from ion_vcf.ion_vcf import IonVcf
from ion_vcf.conversion import VcfConverter
from ion_vcf import __version__

supported_ir_vcf_versions = ['0.1.2', '0.1.4', '0.1.5']


def main(args_text=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            '''
            Oncomine(R) VCF Converter
            -----------------------
            Converts VCF files output by Ion Reporter(TM) sequencing software
            into a TSV file broken out by alternate alleles.
            '''
        )
    )

    parser.add_argument(
        '--input', '-i', required=True, help='VCF file to convert', metavar='<VCF file>', dest='vcf_file_name')

    parser.add_argument('--output', '-o', help='TSV file to write', metavar='<TSV file>', dest='tsv_file_name')

    parser.add_argument(
        '--column-list-file', '-c', help='TXT file with one field per line to include in output file',
        metavar='<column list file>', dest='column_file_name'
    )

    parser.add_argument(
        '--force', '-f', help='Force output to overwrite previous output, if any exists', action='store_true',
        dest='force_output_overwrite'
    )

    parser.add_argument(
        '--all-genes', '-a', help='Keep annotations for all genes in a record\'s FUNC block. Default is to keep '
                                  'only Oncomine genes', action='store_true', dest='keep_all_genes'
    )

    parser.add_argument(
        '--all-cnvs', help='Keep all CNV records in the output. Default is to remove CNVs with no gene associated',
        action='store_true', dest='keep_all_cnvs'
    )

    parser.add_argument(
        '--meta', '-m',
        help='Include metadata fields from the VCF file. Optionally specify a comma-separated list of metadata fields '
             'to include. If no list is provided, the following fields will be included: sampleGender, '
             'sampleDiseaseType, CellularityAsAFractionBetween0-1, TotalMappedFusionPanelReads, mapd.',
        metavar='<list of metadata fields>', nargs='?', dest='meta', default=False
    )

    parser.add_argument('--version', '-v', action='version', version='%(prog)s {version}'.format(version=__version__))

    args = parser.parse_args(args_text.split() if args_text is not None else None)

    vcf_object = IonVcf.create_from_vcf_file(args.vcf_file_name)
    converter = VcfConverter()

    output_file_name = args.tsv_file_name if args.tsv_file_name else args.vcf_file_name.replace('.vcf', '.tsv')

    if os.path.exists(output_file_name) and not args.force_output_overwrite:
        sys.exit('A file or folder with the name \'{tsv}\' already exists. Use --force to overwrite.'.format(
            tsv=output_file_name))
    else:
        columns_to_include = []
        if args.column_file_name:
            if os.path.isfile(args.column_file_name):
                with open(args.column_file_name, 'r') as column_file:
                    columns_to_include = [column.rstrip('\r\n') for column in column_file.readlines()]
            else:
                sys.exit('The column list file \'{file}\' does not exist!'.format(file=args.column_file_name))
        allele_records = converter.convert(
            vcf_object, keep_all_genes=args.keep_all_genes, keep_all_cnvs=args.keep_all_cnvs)

        if vcf_object.ir_vcf_version not in supported_ir_vcf_versions:
            sys.exit('Oncomine(R) VCF Converter expects an IR VCF with IonReporterExportVersion of {vcf_version}.  '
                     'Input VCF IonReporterExportVersion: {actual_version}.'
                     .format(vcf_version=' or '.join(supported_ir_vcf_versions),
                             actual_version=vcf_object.ir_vcf_version))

        meta_fields = None
        if args.meta is not None:
            meta_fields = [f.strip() for f in args.meta.split(',')] if args.meta else []

        converter.write_to_file(
            output_file_name, allele_records, vcf_object.metadata_raw, meta_fields, columns_to_include)

if __name__ == '__main__':
    main()
