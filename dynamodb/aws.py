import boto3
import os
import json
import zipfile

AWS_RESOURCE = 'dynamodb'


def aws_credentials():
    s3_conf = '../resources/.aws_credentials.json'
    curr_dir = os.path.dirname(__file__)
    file_name = os.path.join(curr_dir, s3_conf)
    if not os.path.isfile(file_name):
        print 'aws config file missing.'
        return
    with open(file_name) as config_file:
        config = json.load(config_file)
        #print config
        if 'aws_access_key_id' not in config or 'aws_secret_access_key' not in config:
            print 'aws credentials not found.'
            return
        return config['aws_access_key_id'], config['aws_secret_access_key']



class DynamoDBService(object):

    def __init__(self):
        self.__access_key, self.__secret_key = aws_credentials()

    def get_db_connection(self):
        try:
            ddb = boto3.resource(AWS_RESOURCE,
                                 aws_access_key_id=self.__access_key,
                                 aws_secret_access_key=self.__secret_key,
                                 region_name='us-west-2')
        except:
            print 'S3 connection cannot be established. Please double check your credentials and network connection.'
            return None
        return ddb

    @staticmethod
    def get_local_connection():
        try:
            ddb = boto3.resource(AWS_RESOURCE, endpoint_url='http://localhost:8000', region_name='us-west-2')
        except:
            print 'S3 local connection cannot be established. Please double check your credentials and network connection.'
            return None
        return ddb

    def list_all_tables(self):
        client = boto3.client(AWS_RESOURCE,
                              aws_access_key_id=self.__access_key,
                              aws_secret_access_key=self.__secret_key,
                              region_name='us-west-2')
        tables = client.list_tables()
        return tables

    def validate_msn(msn):
        db_service = DynamoDBService()
        dynamo_db = db_service.get_db_connection()
        control_table = dynamo_db.Table('sampleControl')
        response = control_table.query(
            KeyConditionExpression=Key('_id').eq('_'.join(msn.split('_')[1:]))
        )
        return response['Items'] > 0

    #     ddb = self.get_db_connection()
    #     ddb.q







