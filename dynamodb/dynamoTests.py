import aws
from aws import DynamoDBService
import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr
import sys

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


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
    dynamo_db = db_service.get_local_connection()
    table = dynamo_db.create_table(
        TableName=table_name,
        KeySchema=[
        { 'AttributeName': 'site',
          'KeyType': 'HASH'},
        { 'AttributeName': 'date_molecular_id_created',
          'KeyType': 'RANGE' }
    ],
        AttributeDefinitions=[
        { 'AttributeName': 'site',
          'AttributeType': 'S' },
        { 'AttributeName': 'date_molecular_id_created',
          'AttributeType': 'S' }
    ],
        ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
    )
    print('Table status:', table.table_status)

def load_items(json_file, table_name):
    db_service = DynamoDBService()
    dynamo_db = db_service.get_local_connection()
    control_table = dynamo_db.Table(table_name)

    with open(json_file) as json_f:
        sample_ctrls = json.load(json_f)
        items = sample_ctrls['Items']
        for item in items:
        # _id = sample_ctrl['_id']
        # _class = sample_ctrl['_class']
        # molecularSequenceNumber = sample_ctrl['molecularSequenceNumber']
        # dateCreated = sample_ctrl['dateCreated']
        # dateReceived = sample_ctrl['dateReceived']
        # site = sample_ctrl['site']
        # siteIpAddress = sample_ctrl['siteIpAddress']
        # positiveControlVersion = int(sample_ctrl['positiveControlVersion'])
        # positiveControlDateLoaded = sample_ctrl['positiveControlDateLoaded']
        # status = sample_ctrl['status']
        # passed = bool(sample_ctrl['passed'])
        # nextGenerationSequence = sample_ctrl['nextGenerationSequence']

            print 'adding sample control:', item["molecular_id"], item['type']

            control_table.put_item(
                Item={
                    "date_molecular_id_created": item["date_molecular_id_created"],
                    "type": item["type"],
                    "site_ip_address": item["site_ip_address"],
                    "molecular_id": item["molecular_id"],
                    "site": item["site"]
                }
        )

def query_items(table_name):
    db_service = DynamoDBService()
    dynamo_db = db_service.get_local_connection()
    table = dynamo_db.Table(table_name)

    query_str = '{"site":"MoCha","type":"positive"}'
    print "filter_condition: Attr('site').eq('MoCha')&Attr('type').eq('positive')"
    attrs = json.loads(query_str)
    fe = None
    for attr in attrs:
        if fe == None:
            fe = Attr(attr).eq(attrs[attr])
        else:
            fe = fe & Attr(attr).eq(attrs[attr])

    response = table.scan(
        FilterExpression=fe,
    )

    for i in response['Items']:
        print(json.dumps(i, cls=DecimalEncoder))

    while 'LastEvaluatedKey' in response:
        response = table.scan(
            ProjectionExpression=pe,
        )

        for i in response['Items']:
            print(json.dumps(i, cls=DecimalEncoder))





# def validate_item(msn):
#     db_service = DynamoDBService()
#     dynamo_db = db_service.get_db_connection()
#     control_table = dynamo_db.Table('sampleControl')
#     response = control_table.query(
#         KeyConditionExpression=Key('_id').eq('_'.join(msn.split('_')[1:]))
#     )
#     return response['Items'] > 0




if __name__ == '__main__':
    table_name = sys.argv[1]
    #query_items(table_name)

    #test_production()
    print 'creating table:'+ table_name
    create_table(table_name)

    print 'loading some items:'
    load_items('tst_load.json', table_name)

    print 'query demo:'
    query_items(table_name)

    #print validate_item('SampleControl_MDACC_1')


