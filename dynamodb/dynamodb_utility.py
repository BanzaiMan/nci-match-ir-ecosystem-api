import aws
from aws import DynamoDBService
from boto3.dynamodb.conditions import Key, Attr



PED_MATCH_POSITIVE_CONTROL_URL_BASE = 'http://pedmatch.org:10250/nci-match-rules/rules/rs/variantReportForPositiveSampleControl?'

def create_table(table_name, partition_key_name, partition_attribute_type, sort_key_name, sort_attribute_type, read_capacity_units, write_capacity_units):
    db_service = DynamoDBService()
    dynamo_db = db_service.get_db_connection()
    table = dynamo_db.create_table(
        TableName=table_name,
        KeySchema=[
            { 'AttributeName': partition_key_name,
              'KeyType': 'HASH'},
            { 'AttributeName': sort_key_name,
              'KeyType': 'RANGE' }
        ],
        AttributeDefinitions=[
            { 'AttributeName': partition_key_name,
              'AttributeType': partition_attribute_type },
            { 'AttributeName': sort_key_name,
              'AttributeType': sort_attribute_type }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': read_capacity_units,
            'WriteCapacityUnits': write_capacity_units
        }
    )
    print('Table status:', table.table_status)

def delete_table(table_name):
    db_service = DynamoDBService()
    dynamo_db = db_service.get_db_connection()
    table = dynamo_db.Table(table_name)
    table.delete()

def load_item_primary_key(table_name, partition_key_name, partition_key_value, sort_key_name, sort_key_value):
    db_service = DynamoDBService()
    dynamo_db = db_service.get_db_connection()
    table = dynamo_db.Table(table_name)
    table.put_item(
        Item={
            partition_key_name: partition_key_value,
            sort_key_name:      sort_key_value
        }
    )
    print "Loaded partition key " + partition_key_name + " with value " + partition_key_value + " in table " + table_name
