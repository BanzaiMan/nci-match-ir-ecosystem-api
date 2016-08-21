from boto3.dynamodb.conditions import Attr
import json


class QueryHelper(object):

    @staticmethod
    def create_filter_expression(multidict_query):

        filter_expression = None
        for key, value in multidict_query.iteritems(multi=False):
            if filter_expression is not None:
                filter_expression = filter_expression & Attr(key).eq(value)
            else:
                filter_expression = Attr(key).eq(str(value))

        return filter_expression

if __name__ == '__main__':
    my_json = '{"site":"MoCha","type":"positive"}'
    fe = QueryHelper.create_filter_expression(my_json)
    print type(fe)


