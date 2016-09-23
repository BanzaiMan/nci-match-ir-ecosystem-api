import boto3
from abc import ABCMeta, abstractmethod
from botocore.exceptions import ClientError
import logging
from common.query_helper import QueryHelper


class DynamoDBAccessor(object):
    __metaclass__ = ABCMeta

    """Generic class for working with Dynamodb tables. Nothing in this class should refer to a specific table
    or hard code any attribute. Further, this class should never be directly called from the main application, only
    resources. To use this class declare a child class in the resource directory and instantiate instances of that
    class. Only overwrite in child class the methods in here when necessary."""

    @abstractmethod
    def __init__(self, table, url='http://localhost:8000', region='us-east-1'):
        self.url = url
        self.region = region
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region, endpoint_url=self.url)
        self.client = boto3.client('dynamodb', region_name=self.region, endpoint_url=self.url)
        self.logger.info("Checking database for table existence.")
        self.table = self.handle_table_creation(table)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("DynamoDBAccessor instantiated")

    # Used to get items without regard to keys from table based on some parameters
    def scan(self, query_parameters, projection, *exclusive_start_key):
        if query_parameters is not None:
            self.logger.debug("Dynamodb SCAN with filter expression(s) called")
            self.logger.debug(str(query_parameters))
            if any(exclusive_start_key):
                self.logger.debug("Exclusive start key is " + str(exclusive_start_key[0]))
                try:
                    if len(projection) > 0:
                        results = self.table.scan(FilterExpression=QueryHelper.create_filter_expression(query_parameters),
                                                  ExclusiveStartKey=exclusive_start_key[0],
                                                  ProjectionExpression=projection)
                    else:
                        results = self.table.scan(
                            FilterExpression=QueryHelper.create_filter_expression(query_parameters),
                            ExclusiveStartKey=exclusive_start_key[0])
                except Exception as e:
                    self.logger.error("Scan of database failed because " + e.message)
                    raise
            else:
                self.logger.debug("Scan with no start key")
                try:
                    if len(projection) > 0:
                        results = self.table.scan(
                            FilterExpression=QueryHelper.create_filter_expression(query_parameters),
                            ProjectionExpression=projection)
                    else:
                        results = self.table.scan(
                            FilterExpression=QueryHelper.create_filter_expression(query_parameters))
                except Exception as e:
                    self.logger.error("Scan of database failed because " + e.message)
                    raise
        else:
            self.logger.debug("IR Ecosystem scan without query_parameters, returning all records")
            if any(exclusive_start_key):
                self.logger.debug("Exclusive start key is " + str(exclusive_start_key[0]))
                try:
                    if len(projection) > 0:
                        results = self.table.scan(ExclusiveStartKey=exclusive_start_key[0],
                                                  ProjectionExpression=projection)
                    else:
                        results = self.table.scan(ExclusiveStartKey=exclusive_start_key[0])
                except Exception as e:
                    self.logger.error("Scan of database failed because " + e.message)
                    raise
            else:
                try:
                    if len(projection) > 0:
                        results = self.table.scan(ProjectionExpression=projection)
                    else:
                        results = self.table.scan()
                except Exception as e:
                    self.logger.error("Scan of database failed because " + e.message)
                    raise

        # NOTE that this method is recursive and will call itself in the event that their is over 1 MB of data returned
        items = results['Items'] if len(results) > 0 else []
        if results.get('LastEvaluatedKey'):
            try:
                items += self.scan(query_parameters, projection, results['LastEvaluatedKey'])
            except Exception as e:
                self.logger.error("Scan of database failed because " + e.message)
                raise

        return items

    # To be confusing, "putting an item" in dynamodb terms is creating a record. Yet in Rest terms this is
    # usually a POST whereas, in rest terms, a PUT is usually updating an item. So they mean different things in
    # in different context.
    # TODO: Add support for additional keys
    def put_item(self, item_dictionary):
        self.logger.debug("Dynamodb put_item called")
        self.logger.debug(str(item_dictionary))
        try:
            return self.table.put_item(Item=item_dictionary)
        except ClientError as e:
            self.logger.debug("Client Error on put_item: " + e.message)
            raise

    # Updating an item does exactly that...in REST terms this is more often a "PUT" but in dynamodb put means create as
    # noted above. Confusing yes. Just have to keep context straight.
    def update_item(self, item_dictionary, key, *additional_keys):
        self.logger.debug("Dynamodb update_item called")
        update_expression, expression_attribute_values = QueryHelper.create_update_expression(item_dictionary)

        self.logger.debug("key:" + str(key) + "::Items to update: " + str(expression_attribute_values))
        if not additional_keys:
            all_keys = QueryHelper.create_key_dict('update', key)
        else:
            all_keys = QueryHelper.create_key_dict('update', key)

        self.logger.debug("Key=" + str(all_keys))
        self.logger.debug("UpdateExpression=" + str(update_expression))
        self.logger.debug("ExpressionAttributeValues=" + str(expression_attribute_values))
        try:
            return self.table.update_item(Key=all_keys, UpdateExpression=update_expression,
                                          ExpressionAttributeValues=expression_attribute_values)
        except ClientError as e:
            self.logger.error("Client Error on update_item: " + e.message)
            raise

    # this function and delete_item are essentially the same except the function name
    # Used to get a single item by ID from the table
    def get_item(self, key, projection, *additional_keys):
        try:
            results = self.__item(self.table.get_item, 'get', key, projection, additional_keys)
            return results['Item'] if 'Item' in results else []
        except ClientError as e:
            self.logger.error("Client Error on get_item: " + e.message)
            raise

    # this function and get_item are essentially the same except the function name
    # so I'm performing a little python magic by passing the actual function to another function
    def delete_item(self, key, *additional_keys):
        try:
            return self.__item(self.table.delete_item, 'delete', key, additional_keys)
        except ClientError as e:
            self.logger.error("Client Error on delete_item: " + e.message)
            raise

    # This is used to write a lot of data to the database at one time. Good for loading the database from a backup
    # or loading with test data.
    def batch_writer(self, items_list_dictionary):
        with self.table.batch_writer() as batch:
            for item in items_list_dictionary:
                try:
                    batch.put_item(Item=item)
                except ClientError as e:
                    self.logger.error("Client Error on put_item: " + e.message)
                    raise

    # Does what it says..kaboom
    def delete_table(self):
        try:
            self.table.delete()
        except ClientError as e:
            self.logger.error("Client Error on deleting table: " + e.message)
            raise

    # This is a little piece of OO magic. Essentially it creates a table by ensuring/enforcing the concept
    # that subclasses/children must implement the batch_delete method. The code shown below should never
    # be able to be called.
    @abstractmethod
    def batch_delete(self, query_parameters):
        """Each concrete class must know the specifics on how to delete items in batch because this
        requires knowledge of the tables key, which would be consulted to discover generically."""
        self.logger.error("Batch delete called on dynamodb...this shouldn't be possible")
        return NotImplementedError

    # This is a little piece of OO magic. Essentially it creates a table by ensuring/enforcing the concept
    # that subclasses/children must implement the create_table method. The code shown below should never
    # be able to be called.
    @abstractmethod
    def create_table(self, table_name):
        """Each concrete class must know the specifics on how to create themselves."""
        self.logger.error("create_table called on dynamodb...this shouldn't be possible")
        return NotImplementedError

    # Goes with the table creation and calls the subclasses create_table method. Each subclass should know how
    # to create themselves.
    def handle_table_creation(self, table_name):
        try:
            table_description = self.client.describe_table(TableName=table_name)
            self.logger.info("Table found on system: " + table_name + " :Description: " + str(table_description))
        except Exception as e:
            self.logger.debug(e.message)
            return self.create_table(table_name)

        return self.dynamodb.Table(table_name)

    # This function supports the DRY principle and allows me to consolidate the delete and get code into one.
    def __item(self, function, function_description, key, projection, *additional_keys):
        self.logger.debug("Dynamodb " + function_description + "_item with Keys called")
        self.logger.debug(str(key))
        all_keys = QueryHelper.create_key_dict(function_description, key)

        self.logger.debug("Performing item " + function_description + " from table: " + self.table.name)

        try:
            if len(projection) > 0:
                return function(Key=all_keys, ProjectionExpression=projection)
            else:
                return function(Key=all_keys)
        except ClientError as e:
            self.logger.error("Client Error on " + function_description + ": " + e.message)
            raise
