#!/usr/bin/env python

from distutils.core import setup

from ion_vcf import __version__

setup(
    name='oncomine-vcf-converter',
    version=__version__,
    description='Oncomine(R) VCF Converter',
    long_description=open('README.txt').read(),
    author='Thermo Fisher Scientific Inc.',
    author_email='ann_dev@lifetech.com',
    url='http://en.wikipedia.org/wiki/Variant_Call_Format',
    packages=['ion_vcf', 'ion_vcf.test'],
    package_dir={'ion_vcf': 'ion_vcf', 'ion_vcf.test': 'ion_vcf/test'},
    package_data={
        'ion_vcf': ['oncomine_genes.txt'],
        'ion_vcf.test': ['*.vcf', '*.tsv'],
    },
    scripts=['scripts/convert_vcf.py']
)
