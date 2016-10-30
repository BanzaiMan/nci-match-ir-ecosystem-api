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
        ('get', {'ion_reporter_id': 'IR_K8CVV'}, {}, {'ion_reporter_id': 'IR_K8CVV'}),
        ('get', {'molecular_id': 'SC_K8CVV'}, {'control_type': 'positive'}, {'control_type': 'positive', 'molecular_id': 'SC_K8CVV'}),
        ('get', None, {'control_type': 'positive'},"'NoneType' object has no attribute 'copy'"),
    )
    @unpack
    def test_create_key_dict(self, function_description, key, additional_keys, return_result):
        try:
            return_value = QueryHelper.create_key_dict(function_description, key, **additional_keys)
            print "return data=" + str(return_value)
            assert return_result == return_value
        except AttributeError, e:
            print e
            assert (e.message == return_result)

    # @data(
    #     ({'ion_reporter_id': u'IR_AIO78'}, "'set ion_reporter_id =:ion_reporter_id', {u':ion_reporter_id': u'IR_AIO78'}"),
    #     ({'ion_reporter_id': None}, "'set ion_reporter_id =:ion_reporter_id', {u':ion_reporter_id': u'None'}"),
    #     ({None: u'IR_AIO78'}, "'set None =:None', {u':None': u'IR_AIO78'}"),
    #     ({None: None}, "'set None =:None', {u':None': u'None'}"),
    #     (None, "'NoneType' object has no attribute 'iteritems'")
    # )
    # @unpack
    # def test_create_update_expression(self, multidict_query, return_result):
    #     try:
    #         return_value = QueryHelper.create_update_expression(multidict_query)
    #         print "return data=" + str(return_value)
    #         assert return_result in str(return_value)
    #     except Exception, e:
    #         print e
    #         assert str(e) == return_result

# if __name__ == '__main__':
#     unittest.main()

