import unittest
from ddt import ddt, data, unpack
from common.dictionary_helper import DictionaryHelper


@ddt
class TestDictionaryHelper(unittest.TestCase):
    @data(({'dic1': 'a'}, True), ('', False), ({}, False), (None, False))
    @unpack
    def test_has_values(self, dic1, expected_results):

        assert DictionaryHelper.has_values(dic1) == expected_results

    @data(
        ({'a': None, 'b': 1, 'c': 2}, {'a': 'b'}, False),
        ({'a': None, 'b': 1, 'c': 2}, {'b': 'd'}, True),
        ({'a': 'x', 'b': 'y', 'c': 'z'}, {'b': 'c'}, True)
    )
    @unpack
    def test_keys_have_value(self, test_dic, key, result):
        print DictionaryHelper.keys_have_value(test_dic, key)
        assert DictionaryHelper.keys_have_value(test_dic, key) == result


if __name__ == '__main__':
    unittest.main()
