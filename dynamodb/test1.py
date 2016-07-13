import aws
from aws import DynamoDBService
from boto3.dynamodb.conditions import Key, Attr

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



if __name__ == '__main__':

    test_local()
    #test_production()


    #prod_conn = DynamoDBService.get_db_connection()
    #print prod_conn.tables.all()

