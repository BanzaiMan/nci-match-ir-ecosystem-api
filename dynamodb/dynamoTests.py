import aws
from aws import DynamoDBService
from boto3.dynamodb.conditions import Key, Attr
import json

def test_local():
    local_conn = DynamoDBService.get_local_connection()
    table = local_conn.Table('sampleControl')
    print table
    response = table.scan(
        FilterExpression=Attr('molecularSequenceNumber').eq('SampleControl_MDACC_1')
    )
    print response
    items = response['Items']
    print 'items found:', items

def test_production():
    db_service = DynamoDBService()
    print db_service.list_all_tables()
    #prod_conn = db_service.get_db_connection()

def create_table(table_name):
    db_service = DynamoDBService()
    dynamo_db = db_service.get_db_connection()
    table = dynamo_db.create_table(
        TableName=table_name,
        KeySchema=[
        { 'AttributeName': '_id',
          'KeyType': 'HASH'},
        { 'AttributeName': '_class',
          'KeyType': 'RANGE' }
    ],
        AttributeDefinitions=[
        { 'AttributeName': '_id',
          'AttributeType': 'S' },
        { 'AttributeName': '_class',
          'AttributeType': 'S' }
    ],
        ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
    )
    print('Table status:', table.table_status)

def load_item(json_file):
    db_service = DynamoDBService()
    dynamo_db = db_service.get_db_connection()
    control_table = dynamo_db.Table('sampleControl')

    with open(json_file) as json_f:
        sample_ctrl = json.load(json_f)
        _id = sample_ctrl['_id']
        _class = sample_ctrl['_class']
        molecularSequenceNumber = sample_ctrl['molecularSequenceNumber']
        dateCreated = sample_ctrl['dateCreated']
        dateReceived = sample_ctrl['dateReceived']
        site = sample_ctrl['site']
        siteIpAddress = sample_ctrl['siteIpAddress']
        positiveControlVersion = int(sample_ctrl['positiveControlVersion'])
        positiveControlDateLoaded = sample_ctrl['positiveControlDateLoaded']
        status = sample_ctrl['status']
        passed = bool(sample_ctrl['passed'])
        nextGenerationSequence = sample_ctrl['nextGenerationSequence']

        print 'adding sample control:'+molecularSequenceNumber

        control_table.put_item(
            Item={
                '_id': _id,
                '_class': _class,
                'molecularSequenceNumber': molecularSequenceNumber,
                'dateCreated': dateCreated,
                'dateReceived': dateReceived,
                'site': site,
                'siteIpAddress': siteIpAddress,
                'positiveControlVersion': positiveControlVersion,
                'positiveControlDateLoaded': positiveControlDateLoaded,
                'status': status,
                'passed': passed,
                'nextGenerationSequence': nextGenerationSequence
            }
        )


def validate_item(msn):
    db_service = DynamoDBService()
    dynamo_db = db_service.get_db_connection()
    control_table = dynamo_db.Table('sampleControl')
    response = control_table.query(
        KeyConditionExpression=Key('_id').eq('_'.join(msn.split('_')[1:]))
    )
    return response['Items'] > 0




if __name__ == '__main__':

    #test_production()
    #create_table('sampleControl')
    #load_item('/Users/sunq3/match_data/sampleControl/s2.txt')
    print validate_item('SampleControl_MDACC_1')


