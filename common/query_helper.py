from boto3.dynamodb.conditions import Attr
import logging
import json
from datetime_helper import DateTimeHelper


class QueryHelper(object):

    @staticmethod
    def create_filter_expression(multidict_query):
        logger = logging.getLogger(__name__)
        logger.debug("Filter expression being created")
        logger.debug(str(multidict_query))

        filter_expression = None
        #for key, value in multidict_query.iteritems(multi=False):
        for key, value in multidict_query.iteritems():
            if filter_expression is not None:
                filter_expression = filter_expression & Attr(key).eq(value)
            else:
                filter_expression = Attr(key).eq(str(value))

        logger.debug("Filter expression created: " + str(filter_expression))
        return filter_expression

    @staticmethod
    def create_key_dict(function_description, key, *additional_keys):
        logger = logging.getLogger(__name__)
        logger.debug("Key dictionary being created")
        logger.debug(str(key))

        all_keys = key.copy()
        if not all(additional_keys):
            logger.debug("Additional Keys used in " + function_description + ": " + str(additional_keys))
            all_keys.update(additional_keys)

        logger.debug("Key dictionary created: " + str(all_keys))
        return all_keys

    @staticmethod
    def create_update_expression(multidict_query):
        logger = logging.getLogger(__name__)
        logger.debug("Update expression and attribute values being created")
        logger.debug(str(multidict_query))

        update_expression = "set " + (', '.join(str(key) + " =:" + str(key) for key, value in multidict_query.iteritems()))
        update_expression_attribute_values = (', '.join("\":" + str(key) + "\": \"" + str(value) + "\""
                                                        for key, value in multidict_query.iteritems()))

        logger.debug("Update expression created: " + str(update_expression))
        logger.debug("Update expression attribute values created: " + str(update_expression_attribute_values))
        exp = '{'+update_expression_attribute_values+'}'
        logger.debug(exp)
        return update_expression, json.loads(exp)

