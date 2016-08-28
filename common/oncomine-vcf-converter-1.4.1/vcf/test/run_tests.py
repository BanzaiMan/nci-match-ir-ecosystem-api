#!/usr/bin/env python

import os
import sys
import unittest
import importlib
import tempfile
import shutil


def main():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    module_dir = os.path.dirname(this_dir)
    package_dir = os.path.dirname(module_dir)
    sys.path.append(package_dir)
    os.environ['OVCF_TEST_TEMPDIR'] = tempfile.mkdtemp(prefix='Oncomine_VCF_Converter_Tests_')
    print 'OVCF_TEST_TEMPDIR: ' + os.environ['OVCF_TEST_TEMPDIR'] + '\n'

    suites = []
    for test_file in os.listdir(os.path.dirname(os.path.abspath(__file__))):
        if test_file.startswith('test_') and test_file.endswith('.py'):
            test_module_name = 'vcf.test.{module}'.format(module=os.path.basename(test_file).split('.')[0])
            test_module = importlib.import_module(test_module_name)
            include_test = not hasattr(test_module, 'include') or test_module.include
            if include_test:
                if hasattr(test_module, 'suite') and callable(getattr(test_module, 'suite')):
                    test_module.suite()
                suites.append(unittest.defaultTestLoader.loadTestsFromName(test_module_name))

    full_suite = unittest.TestSuite(suites)
    test_result = unittest.TextTestRunner(verbosity=2).run(full_suite)

    if len(test_result.failures) > 0:
        sys.exit('')

    if os.path.exists(os.environ['OVCF_TEST_TEMPDIR']):
        shutil.rmtree(os.environ['OVCF_TEST_TEMPDIR'])
    del os.environ['OVCF_TEST_TEMPDIR']


if __name__ == '__main__':
    main()