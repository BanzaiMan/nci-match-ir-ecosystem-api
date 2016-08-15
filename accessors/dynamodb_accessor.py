import boto3
import os
import json
import zipfile

from boto3.dynamodb.conditions import Key

AWS_RESOURCE = 'dynamodb'





class DynamoDBAccessor(object):
    my_sqs = boto3.resource('sqs', region_name='us-west-2')

    def __init__(self):
        self.__access_key, self.__secret_key, self.__region_name = aws_credentials()

    @staticmethod
    def aws_credentials():
        s3_conf = '../resources/.aws_credentials.json'
        curr_dir = os.path.dirname(__file__)
        file_name = os.path.join(curr_dir, s3_conf)
        if not os.path.isfile(file_name):
            print 'aws config file missing.'
            return
        with open(file_name) as config_file:
            config = json.load(config_file)
            # print config
            if 'aws_access_key_id' not in config or 'aws_secret_access_key' not in config or 'region_name' not in config:
                print 'aws credentials not found.'
                return
            return config['aws_access_key_id'], config['aws_secret_access_key'], config['region_name'],

    def get_db_connection(self):
        try:
            ddb = boto3.resource(AWS_RESOURCE,
                                 aws_access_key_id=self.__access_key,
                                 aws_secret_access_key=self.__secret_key,
                                 region_name=self.__region_name)
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

    # def validate_msn(msn):
    #     db_service = DynamoDBService()
    #     dynamo_db = db_service.get_db_connection()
    #     control_table = dynamo_db.Table('sampleControl')
    #     response = control_table.query(
    #         KeyConditionExpression=Key('_id').eq('_'.join(msn.split('_')[1:]))
    #     )
    #     return response['Items'] > 0
    #
    # #     ddb = self.get_db_connection()
    #     ddb.q







