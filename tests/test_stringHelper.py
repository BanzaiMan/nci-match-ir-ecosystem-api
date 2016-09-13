import unittest
from mock import patch
import string

from common.string_helper import StringHelper
from ddt import ddt, data, unpack


@ddt
class TestStringHelper(unittest.TestCase):

    @patch('common.string_helper.StringHelper.generate_random_string')
    def test_generate_molecular_id(self, random_string_function):
        random_string_function.return_value = "TR45G"
        random_string = StringHelper.generate_molecular_id(5)
        assert random_string.startswith("SC_")

    @patch('common.string_helper.StringHelper.generate_random_string')
    def test_generate_ion_reporter_id(self, random_string_function):
        random_string_function.return_value = "WO85G"
        random_string = StringHelper.generate_ion_reporter_id(5)
        assert random_string.startswith("IR_")

    @data((5, 5, ""),
          (0, "", "Invalid Input"),
          (8, 8, ""),
          (-1, "", "Invalid Input"),
          ("dog", "", "Invalid Input"),
          (5.032, "", "Invalid Input"))
    @unpack
    def test_generate_random_string(self, random_length, expected_length, exception_message):
        try:
            random_string = StringHelper.generate_random_string(random_length)
            assert len(random_string) == expected_length
            for m in random_string:
                assert (m in string.ascii_uppercase or m in string.digits)
        except ValueError, e:
            assert (e.message == exception_message)

if __name__ == '__main__':
    unittest.main()
