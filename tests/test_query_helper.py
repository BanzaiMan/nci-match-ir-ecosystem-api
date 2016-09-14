import unittest

from ddt import ddt, data, unpack
from mock import patch
from common.query_helper import QueryHelper


@ddt
class TestQueryHelper(unittest.TestCase):
    @data(
        ({'ion_reporter_id': u'IR_AIO78'}, '<boto3.dynamodb.conditions.Equals object at'),
        ({'ion_reporter_id': None}, 'Must pass in a dictionary or mutlidict_query'),
        ({None: u'IR_AIO78'}, '<boto3.dynamodb.conditions.Equals object at'),
        ({None: None}, 'Must pass in a dictionary or mutlidict_query'),
        (None, 'Must pass in a dictionary or mutlidict_query')
    )
    @unpack
    def test_create_filter_expression(self, multidict_query, return_result):
        try:
            return_value = QueryHelper.create_filter_expression(multidict_query)
            print "return data=" + str(return_value)
            assert return_result in str(return_value)
        except Exception, e:
            print e
            assert str(e) == return_result


    @data(
        ('get', {'ion_reporter_id': 'IR_K8CVV'}, '(((),),)', {'ion_reporter_id': 'IR_K8CVV'}),
    )
    @unpack
    def test_create_key_dict(self, function_description, key, additional_keys, return_result):
        try:
            return_value = QueryHelper.create_key_dict(function_description, key, additional_keys)
            print "return data=" + str(return_value)
            assert return_result == return_value
        except AttributeError, e:
            assert (e.message == return_result)

if __name__ == '__main__':
    unittest.main()

