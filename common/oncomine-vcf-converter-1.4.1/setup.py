#!/usr/bin/env python

from distutils.core import setup

from vcf import __version__

setup(
    name='oncomine-vcf-converter',
    version=__version__,
    description='Oncomine(R) VCF Converter',
    long_description=open('README.txt').read(),
    author='Thermo Fisher Scientific Inc.',
    author_email='ann_dev@lifetech.com',
    url='http://en.wikipedia.org/wiki/Variant_Call_Format',
    packages=['vcf', 'vcf.test'],
    package_dir={'vcf': 'vcf', 'vcf.test': 'vcf/test'},
    package_data={
        'vcf': ['oncomine_genes.txt'],
        'vcf.test': ['*.vcf', '*.tsv'],
    },
    scripts=['scripts/convert_vcf.py']
)
