import boto3
import logging
from common.query_helper import QueryHelper


class DynamoDBAccessor(object):

    """Generic class for working with Dynamodb tables. Nothing in this class should refer to a specific table
    or hardcode any attribute. Further, this class should never be directly called from the main application, only
    resources. To use this class declare a child class in the resource directory and instantiate instances of that
    class. Only overwrite in child class the methods in here when necessary."""

    def __init__(self, table, url='http://localhost:8000', region='us-east-1'):
        self.url = url
        self.region = region
        self.dynamodb = boto3.resource('dynamodb', region_name=region, endpoint_url=url)
        self.table = self.dynamodb.Table(table)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("DynamoDBAccessor instantiated")

    def scan(self, query_parameters, *exclusive_start_key):
        if query_parameters is not None:
            self.logger.debug("Dynamodb SCAN with filter expression(s) called")
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
