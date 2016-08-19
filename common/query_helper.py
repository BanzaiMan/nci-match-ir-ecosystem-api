from boto3.dynamodb.conditions import Attr
import json

class QueryHelper(object):
    # {'site':'mocha'}
    @staticmethod
    def create_filter_expression(json_string):
        #Todo: json validation
        attrs = json.loads(json_string)
        fe = None
        for attr in attrs:
            if fe:
                fe = fe & Attr(attr).eq(attrs[attr])
            else:
                fe = Attr(attr).eq(attrs[attr])
        return fe

if __name__ == '__main__':
    my_json = '{"site":"MoCha","type":"positive"}'
    fe = QueryHelper.create_filter_expression(my_json)
    print type(fe)


