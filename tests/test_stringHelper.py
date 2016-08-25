import unittest
from mock import patch, MagicMock
import string
import sys
sys.path.append("..")
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

    @data((5, 5, ""), (0, "", "Invalid Input"), (8, 8, ""), (-1, "", "Invalid Input"), ("dog", "", "Invalid Input"))
    @unpack
    def test_generate_random_string(self, random_length, expected_length, exception_message):
        print "Testing if random string and if it contains uppercase letters or numbers"
        try:
            random_string = StringHelper.generate_random_string(random_length)
            assert len(random_string) == expected_length
            for m in random_string:
                assert (m in string.ascii_uppercase or m in string.digits)
        except ValueError, e:
            assert (e.message == exception_message)

if __name__ == '__main__':
    unittest.main()
