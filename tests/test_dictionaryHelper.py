import unittest
import sys
from ddt import ddt, data, unpack

sys.path.append('..')
from common.dictionary_helper import DictionaryHelper


@ddt
class TestDictionaryHelper(unittest.TestCase):
    @data(({'dic1': 'a'}, True), ('', False), ({}, False), (None, False))
    @unpack
    def test_has_values(self, dic1, expected_results):

        assert DictionaryHelper.has_values(dic1) == expected_results

# TODO: Fix, it is not passing in multiple sets of data, correct formatting

    @data(({'a': None, 'b': 1, 'c': 2}, ['a', 'b'], False, ['b', 'd'], False, ['b', 'c'], True))
    @unpack
    def test_keys_have_value(self, test_dic, key1, result1, key2, result2, key3, result3):
        assert DictionaryHelper.keys_have_value(test_dic, key1) == result1
        assert DictionaryHelper.keys_have_value(test_dic, key2) == result2
        assert DictionaryHelper.keys_have_value(test_dic, key3) == result3


if __name__ == '__main__':
    unittest.main()
