import unittest
from mock import patch, MagicMock
import string
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
from common.string_helper import StringHelper
from ddt import ddt, data, unpack

@ddt
class TestStringHelper(unittest.TestCase):

    @patch('common.string_helper.StringHelper.generate_random_string')
    def test_generate_molecular_id(self, random_string_function):
        random_string_function.return_value = "TR45G"
        print "Testing if random string contains 'SC_' in front"
        random_string = StringHelper.generate_molecular_id(5)
        assert random_string.startswith("SC_")

    @data((5,5),(0,0),(8,8))
    @unpack
    def test_generate_random_string(self, random_length, expected_length):
        print "Testing if random string and if it contains uppercase letters or numbers"
        random_string = StringHelper.generate_random_string(random_length)
        assert len(random_string) == expected_length

        for m in random_string:
            assert (m in string.ascii_uppercase or m in string.digits)

if __name__ == '__main__':
    unittest.main()