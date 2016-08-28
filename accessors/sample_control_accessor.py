import logging
import __builtin__
from dynamodb_accessor import DynamoDBAccessor

KEY = 'molecular_id'


class SampleControlAccessor(DynamoDBAccessor):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("SampleControlAccessor instantiated")
        self.logger.debug("__builtin__.environment: " + str(__builtin__.environment))
        self.logger.debug("__builtin__.environment_config: " + str(__builtin__.environment_config))
        DynamoDBAccessor.__init__(self, 'sample_controls',
                                  __builtin__.environment_config[__builtin__.environment]['dynamo_endpoint'],
                                  __builtin__.environment_config[__builtin__.environment]['region'])

    def create_table(self, table_name):
        self.logger.info("Table " + table_name + " not found on system. Create_table called to create it")
        try:
            table = self.dynamodb.create_table(
                TableName=table_name,
                KeySchema=[{'AttributeName': 'molecular_id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'molecular_id', 'AttributeType': 'S'}],
                ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5})
            self.logger.info("Table " + table_name + " created!")
        except Exception, e:
            self.logger.error("create table exception in dynamodb: " + e.message)
            raise

        # wait for confirmation that the table exists
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        self.handle_table_creation(table_name)

    def update(self, item_dictionary):
        sample_control_table_key = str(item_dictionary.pop(KEY))
        self.logger.debug(sample_control_table_key)
        try:
            return self.update_item(item_dictionary, dict(molecular_id=sample_control_table_key))
        except Exception, e:
            self.logger.error("update_item exception in dynamodb: " + e.message)
            raise

    # In order to delete in Dynamodb, first call scan with the query parameters then loop over the returned values
    # and call delete_item on each of them. You can't do deletes directly based on queries like you can in a RDBMS.
    # So this is how you would do it here. The reason this is in the sample_control_accessor instead of in the
    # dynamodb is because this function requires knowledge of the tables KEY so a generic means of doing this isn't
    # as straight forward and is probably overly complicated for our purposes.
    def batch_delete(self, query_parameters):
        items_to_delete = self.scan(query_parameters)
        for item in items_to_delete:
            try:
                self.delete_item({'molecular_id': item[KEY]})
            except Exception, e:
                self.logger.error("Batch delete item exception in dynamodb: " + e.message)
                raise
