import logging
import __builtin__
from dynamodb_accessor import DynamoDBAccessor


class SingleKeyAccessor(DynamoDBAccessor):

    def __init__(self, table_name, key_name):
        self.key_name = key_name
        self.table_name = table_name
        self.logger = logging.getLogger(__name__)
        self.logger.debug("SingleKeyAccessor instantiated")
        DynamoDBAccessor.__init__(self, self.table_name,
                                  __builtin__.environment_config[__builtin__.environment]['dynamo_endpoint'],
                                  __builtin__.environment_config[__builtin__.environment]['region'])

    def create_table(self, table_name):
        self.logger.info("Table " + table_name + " not found on system. Create_table called to create it")
        try:
            table = self.dynamodb.create_table(
                TableName=table_name,
                KeySchema=[{'AttributeName': self.key_name, 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': self.key_name, 'AttributeType': 'S'}],
                ProvisionedThroughput={
                    'ReadCapacityUnits':  __builtin__.environment_config[__builtin__.environment]['read_capacity'],
                    'WriteCapacityUnits': __builtin__.environment_config[__builtin__.environment]['write_capacity']})
            self.logger.info("Table " + table_name + " created!")
        except Exception as e:
            self.logger.error("create table exception in dynamodb: " + e.message)
            raise

        # wait for confirmation that the table exists
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        return self.handle_table_creation(table_name)

    def update(self, item_dictionary):
        table_key = str(item_dictionary.pop(self.key_name))
        self.logger.debug(table_key)
        try:
            return self.update_item(item_dictionary, {self.key_name: table_key})
        except Exception as e:
            self.logger.error("update_item exception in dynamodb: " + e.message)
            raise

    # In order to delete in Dynamodb, first call scan with the query parameters then loop over the returned values
    # and call delete_item on each of them. You can't do deletes directly based on queries like you can in a RDBMS.
    # So this is how you would do it here. The reason this is in the sample_control_accessor instead of in the
    # dynamodb is because this function requires knowledge of the tables KEY so a generic means of doing this isn't
    # as straight forward and is probably overly complicated for our purposes.
    def batch_delete(self, query_parameters):
        items_to_delete = self.scan(query_parameters, '')
        for item in items_to_delete:
            try:
                self.delete_item({self.key_name: item[self.key_name]})
            except Exception as e:
                self.logger.error("Batch delete item exception in dynamodb: " + e.message)
                raise
