from boto3.dynamodb.conditions import Attr

class QueryHelper(object):
    # {'site':'mocha'}
    @staticmethod
    def create_filter_expression(json_string):
        #Todo: Build dynamaically the filter expression
        # fe = Attr('site').eq('mocha') & Attr('id').eq('SC_45RT6')
        fe = True
        return fe