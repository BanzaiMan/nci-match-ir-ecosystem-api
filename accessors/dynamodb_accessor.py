import boto3
import logging
from common.query_helper import QueryHelper


class DynamoDBAccessor(object):

    def __init__(self, table, url='http://localhost:8000', region='us-east-1'):
        self.url = url
        self.region = region
        self.dynamodb = boto3.resource('dynamodb', region_name=region, endpoint_url=url)
        self.table = self.dynamodb.Table(table)
        self.logger = logging.getLogger(__name__)

    def scan(self, query_parameters, *exclusive_start_key):
        if query_parameters is not None:
            self.logger.debug("dynamodb SCAN with filter expression(s) called")
            self.logger.debug(str(query_parameters))
            if not all(exclusive_start_key):
                self.logger.debug("Exclusive start key is " + str(exclusive_start_key))
                results = self.table.scan(FilterExpression=QueryHelper.create_filter_expression(query_parameters),
                                          ExclusiveStartKey=exclusive_start_key)
            else:
                self.logger.debug("Scan with no start key")
                results = self.table.scan(FilterExpression=QueryHelper.create_filter_expression(query_parameters))
        else:
            self.logger.debug("IR Ecosystem scan without query_parameters, returning all records")
            results = self.table.scan()

        items = results['Items']
        if results.get('LastEvaluatedKey'):
            items += self.scan(query_parameters, results['LastEvaluatedKey'])

        return items
