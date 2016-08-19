import boto3
from common.query_helper import QueryHelper


class DynamoDBAccessor(object):

    def __init__(self, table, url='http://localhost:8000', region='us-east-1'):
        self.url = url
        self.region = region
        self.dynamodb = boto3.resource('dynamodb', region_name=region, endpoint_url=url)
        self.table = self.dynamodb.Table(table)

    # Generic Scan Function that handles 1MB limit and returns all results to caller
    # {u'Count': 1, u'Items': [{u'type': u'positive', u'site': u'mocha', u'id': u'SC_45RT6'}], u'ScannedCount': 1,
    #  'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': 'c9207ed1-6f6f-4ea8-bb91-17393b9b3980',
    #                       'HTTPHeaders': {'x-amzn-requestid': 'c9207ed1-6f6f-4ea8-bb91-17393b9b3980',
    #                                       'content-length': '107', 'content-type': 'application/x-amz-json-1.0',
    #                                       'x-amz-crc32': '2945372509', 'server': 'Jetty(8.1.12.v20130726)'}}}
    # have to scan multiple times as data grows because there is 1MB limit on results...add loop to code to handle this
    # using LastEvaluatedKey like this
    # while True:
    #     metadata = response.get('ResponseMetadata', {})
    #     for row in response['Items']:
    #         yield cls.from_row(row, metadata)
    #     if response.get('LastEvaluatedKey'):
    #         response = cls.table().scan(
    #             ExclusiveStartKey=response['LastEvaluatedKey'],
    #         )
    #     else:
    #         break
    #

    def scan(self, query_parameters, *exclusive_start_key):

        if exclusive_start_key is not None:
            results = self.table.scan(FilterExpression=QueryHelper.create_filter_expression(query_parameters),
                                      ExclusiveStartKey=exclusive_start_key)
        else:
            results = self.table.scan(FilterExpression=QueryHelper.create_filter_expression(query_parameters))

        items = results['Items']
        if results.get('LastEvaluatedKey'):
            items += self.scan(query_parameters, results['LastEvaluatedKey'])

        return items
