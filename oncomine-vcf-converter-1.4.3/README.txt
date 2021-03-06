======================
oncomine-vcf-converter
======================

Oncomine(R) VCF Converter::

This package provides utilities for parsing and converting variant call format (VCF)
files generated through Ion Reporter sequencing software.

Information on VCF can be found `here <http://en.wikipedia.org/wiki/Variant_Call_Format>`_.

Installation::

    $ python setup.py install [--user]

This will install the oncomine-vcf-converter package to the Python installation that
the `python` command points to. This package is importable using `import vcf` and includes
VCF parsing modules as well as the conversion module.

In addition, this installation command installs the `convert_vcf.py` script. If using a
Unix-like platform, this script should become globally available, i.e. tab-completing
`conv` should list it. In Windows, the script is installed to the `Scripts` directory
of the Python installation, typically something like C:\Python27\Scripts. The commands
involving the `convert_vcf.py` script below assume a Unix-like platform.

Tests::

Note that if the oncomine-vcf-converter Python package was installed as the root user
the tests will likely need to be run as the root user as well.

    $ cd /path/to/oncomine-vcf-converter-X.X.X
    $ vcf/test/run_tests.py

Help::

    $ convert_vcf.py --help

Examples::

    # Converting a VCF
    $ convert_vcf.py -i sample1.vcf

    # User-defined output file
    $ convert_vcf.py -i input.vcf -o output.tsv

    # Filtering output columns (columns_to_keep.txt is a list of the columns
    # to leave in the ouput file. All columns printed if column list is
    # not provided)
    $ convert_vcf.py -i input.vcf -c columns_to_keep.txt

    # Keeping all CNVs (default is to drop CNVs with no gene)
    $ convert_vcf.py -i input.vcf --all-cnvs

    # Keeping all functional annotations regardless of their gene
    $ convert_vcf.py -i input.vcf -a
