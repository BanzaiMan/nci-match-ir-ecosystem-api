import shutil
import os
import unittest
import tempfile

ENV_VAR_NAME = 'OVCF_TEST_TEMPDIR'

__author__ = 'smatyas'

class BaseTestCase(unittest.TestCase):
    _tmpdir_created_ = False
    OUTPUT_DIR = None
    @classmethod
    def setUpClass(cls):
        print 'setUpClass::%s' % cls.__name__
        ovcf_test_tempdir = os.getenv(ENV_VAR_NAME)

        if ovcf_test_tempdir is None or os.path.exists(ovcf_test_tempdir) is False:
            ovcf_test_tempdir = tempfile.mkdtemp(prefix='Oncomine_VCF_Converter_Tests_')
            cls._tmpdir_created_ = True
            os.environ[ENV_VAR_NAME] = ovcf_test_tempdir

        cls.OUTPUT_DIR = ovcf_test_tempdir

    @classmethod
    def tearDownClass(cls):
        '''Only delete the temp directory if it was created by the BaseTestCase '''
        if not cls._tmpdir_created_:
            return

        print 'tearDownClass::%s' % cls.__name__
        if os.getenv(ENV_VAR_NAME) is not None :

            del os.environ[ENV_VAR_NAME]

        if os.path.exists(cls.OUTPUT_DIR):
            print 'removing tmp dir %s' % os.getenv(ENV_VAR_NAME)
            shutil.rmtree(cls.OUTPUT_DIR)

