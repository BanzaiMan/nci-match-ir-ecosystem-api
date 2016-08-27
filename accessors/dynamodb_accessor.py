import boto3
from abc import ABCMeta, abstractmethod
from botocore.exceptions import ClientError
import logging
from common.query_helper import QueryHelper


class DynamoDBAccessor(object):
    __metaclass__ = ABCMeta

    """Generic class for working with Dynamodb tables. Nothing in this class should refer to a specific table
    or hardcode any attribute. Further, this class should never be directly called from the main application, only
    resources. To use this class declare a child class in the resource directory and instantiate instances of that
    class. Only overwrite in child class the methods in here when necessary."""

    @abstractmethod
    def __init__(self, table, url='http://localhost:8000', region='us-east-1'):
        self.url = url
        self.region = region
        self.dynamodb = boto3.resource('dynamodb', region_name=region, endpoint_url=url)
        self.client = boto3.client('dynamodb', region_name=region, endpoint_url=url)
        self.logger.info("Checking database for sample_control table existence.")
        self.table = self.handle_table_creation(table)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("DynamoDBAccessor instantiated")

    # Used to get items without regard to keys from table based on some parameters
    # TODO: Check for errors on scans
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

    # TODO: Add support for additional keys
    def put_item(self, item_dictionary):
        self.logger.debug("Dynamodb put_item called")
        self.logger.debug(str(item_dictionary))
        try:
            return self.table.put_item(Item=item_dictionary)
        except ClientError, e:
            self.logger.debug("Client Error on put_item: " + e.message)
            raise

    def update_item(self, item_dictionary, key, *additional_keys):
        self.logger.debug("Dynamodb update_item called")
        update_expression, expression_attribute_values = QueryHelper.create_update_expression(item_dictionary)

        self.logger.debug("key:" + str(key) + "::Items to update: " + str(expression_attribute_values))
        if not additional_keys:
            all_keys = QueryHelper.create_key_dict('update', key)
        else:
            all_keys = QueryHelper.create_key_dict('update', key, additional_keys)

        try:
            self.logger.debug("Key=" + str(all_keys))
            self.logger.debug("UpdateExpression=" + str(update_expression))
            self.logger.debug("ExpressionAttributeValues=" + str(expression_attribute_values))
            return self.table.update_item(Key=all_keys, UpdateExpression=update_expression,
                                          ExpressionAttributeValues=expression_attribute_values)
        except ClientError, e:
            self.logger.error("Client Error on update_item: " + e.message)
            raise

    # Used to get a single item by ID from the table
    def get_item(self, key, *additional_keys):
        try:
            return self.__item(self.table.get_item, 'get', key, additional_keys)
        except ClientError, e:
            self.logger.error("Client Error on delete_item: " + e.message)
            raise

    # this function and get_item are essentially the same except the function name
    # so I'm performing a little python magic by passing the actual function to another function
    def delete_item(self, key, *additional_keys):
        try:
            return self.__item(self.table.delete_item, 'delete', key, additional_keys)
        except ClientError, e:
            self.logger.error("Client Error on delete_item: " + e.message)
            raise

    def batch_writer(self, items_list_dictionary):
        with self.table.batch_writer() as batch:
            for item in items_list_dictionary:
                try:
                    batch.put_item(Item=item)
                except ClientError, e:
                    self.logger.error("Client Error on put_item: " + e.message)
                    raise

    def delete_table(self):
        try:
            self.table.delete()
        except ClientError, e:
            self.logger.error("Client Error on deleting table: " + e.message)
            raise

    @abstractmethod
    def create_table(self, table_name):
        """Each concrete class must know the specifics on how to create themselves."""
        self.logger.debug("create_table called on dynamodb...this shouldn't be possible")
        return NotImplementedError

    def __item(self, function, function_description, key, *additional_keys):
        self.logger.debug("Dynamodb " + function_description + "_item with Keys called")
        self.logger.debug(str(key))
        all_keys = QueryHelper.create_key_dict(function_description, key, additional_keys)

        # TODO: Make it print the actual table name being queried
        self.logger.debug("Performing item " + function_description + " from table")

        try:
            return function(Key=all_keys)
        except ClientError, e:
            self.logger.error("Client Error on " + function_description + ": " + e.message)
            raise

    def handle_table_creation(self, table_name):
        try:
            table_description = self.client.describe_table(TableName=table_name)
            self.logger.info("Table found on system: " + table_name + " :Description: " + str(table_description))
        except Exception, e:
            self.logger.debug(e.message)
            return self.create_table(table_name)

        return self.dynamodb.Table(table_name)
