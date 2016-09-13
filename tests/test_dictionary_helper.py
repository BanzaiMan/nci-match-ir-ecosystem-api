import unittest
from ddt import ddt, data, unpack
from common.dictionary_helper import DictionaryHelper


@ddt
class TestDictionaryHelper(unittest.TestCase):
    @data(
        ({'dic1': 'a'}, True),
        ({'dic1': None}, False),
        ('', False),
        ({}, False),
        (None, False)
    )
    @unpack
    def test_has_values(self, dic1, expected_results):
        assert DictionaryHelper.has_values(dic1) == expected_results

    @data(
        ({'a': None, 'b': 1, 'c': 2}, {'a': 'b'}, False),
        ({}, {'b': 'd'}, False),
        ('', {'b': 'd'}, False),
        (None, {'b': 'd'}, False),
        (None, None, False),
        ({'a': None, 'b': 1, 'c': 2}, None, False),
        ({'a': 'x', 'b': 'y', 'c': 'z'}, {'q': 'c'}, False),
        ({'a': 'x', 'b': 'y', 'c': 'z'}, {'b': 'c'}, True)
    )
    @unpack
    def test_keys_have_value(self, test_dic, key, result):
        assert DictionaryHelper.keys_have_value(test_dic, key) == result

if __name__ == '__main__':
    unittest.main()