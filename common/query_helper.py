from boto3.dynamodb.conditions import Attr
import logging


class QueryHelper(object):

    @staticmethod
    def create_filter_expression(multidict_query):
        logger = logging.getLogger(__name__)
        logger.debug("Filter expression being created")
        logger.debug(str(multidict_query))

        filter_expression = None
        for key, value in multidict_query.iteritems(multi=False):
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