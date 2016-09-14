import unittest

from ddt import ddt, data, unpack
from mock import patch
from common.query_helper import QueryHelper


@ddt
class TestQueryHelper(unittest.TestCase):
    # @data(('site', 'MoCha', 'control_type', 'positive'))
    # @unpack
    # def test_create_key_dict(self, key1, value1, key2, value2):
    #     # key1 = 'site'
    #     # value1 = 'MoCha'
    #     # key2 = 'control_type'
    #     # value2 = 'positive'
    #     key_dict = {key1: value1, key2: value2}
    #     # print key_dict
    #     filter_condition = QueryHelper.create_filter_expression(key_dict)
    #     # expected = Attr(key1).eq(value1) & Attr(key2).eq(value2)
    #     # print filter_condition.get_expression() = expected.get_expression()
    #     # print filter_condition.expression_format()
    #     # print filter_condition.
    #     # print filter_condition.get_expression()
    #     # print expected.get_expression()
    #     assert filter_condition.get_expression()['operator'] == 'AND'
    #     assert str(filter_condition.get_expression()['values']).count('boto3.dynamodb.conditions.Equals object at') == 2
    #     assert filter_condition.get_expression()['format'] == '({0} {operator} {1})'

    @data(
        ({'ion_reporter_id': u'IR_AIO78'}, '<boto3.dynamodb.conditions.Equals object at'),
            ({'ion_reporter_id': None}, '<boto3.dynamodb.conditions.Equals object at'),
            ({None: None}, '<boto3.dynamodb.conditions.Equals object at'),
            (None, '<boto3.dynamodb.conditions.Equals object at')
    )
    @unpack
    def test_create_filter_expression(self, multidict_query, return_result):
        try:
            return_value = QueryHelper.create_filter_expression(multidict_query)
            print "return data=" + str(return_value)
            assert return_result in str(return_value)
        except AttributeError, e:
            assert (e.message == "'NoneType' object has no attribute 'iteritems'")

if __name__ == '__main__':
    unittest.main()
