from unittest import TestCase
import unittest
import string
import logging
import sys
sys.path.append('..')
from common.string_helper import StringHelper
from ddt import ddt, data, unpack

@ddt
class TestStringHelper(TestCase):
    def test_generate_molecular_id(self):
        logger = logging.getLogger(__name__)
        logger.info("Testing if random string contains 'SC_' in front")
        random_string = StringHelper.generate_molecular_id(5)
        assert random_string.startswith("SC_")

    @data((5,0,8))
    @unpack
    def test_generate_random_string(self, len1, len2, len3):
        logger = logging.getLogger(__name__)
        logger.info("Testing if random string length equals 5 and if it contains uppercase letters or numbers")

        random_string = StringHelper.generate_random_string()
        assert len(random_string) == len1

        random_string = StringHelper.generate_random_string(len1)
        assert len(random_string) == len1

        random_string = StringHelper.generate_random_string(len2)
        assert random_string == ''

        random_string = StringHelper.generate_random_string(len3)
        assert not len(random_string) == len1

        for m in random_string:
            assert (m in string.ascii_uppercase or m in string.digits)

if __name__ == '__main__':
    unittest.main()