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
    with open(file_name) as config_file:
        config = json.load(config_file)
        if 'aws_access_key_id' not in config or 'aws_secret_access_key' not in config:
            print 'aws credentials not found.'
        return config['aws_access_key_id'], config['aws_secret_access_key']



class DynamoDBService(object):

    def __init__(self):
        self.__access_key, self.__secret_key = aws_credentials()

    def get_db_connection(self):
        try:
            ddb = boto3.resource(AWS_RESOURCE, aws_access_key_id=self.__access_key, aws_secret_access_key=self.__secret_key)
        except:
            print 'S3 connection cannot be established. Please double check your credentials and network connection.'
            return None
        return ddb

    @staticmethod
    def get_local_connection():
        try:
            ddb = boto3.resource(AWS_RESOURCE, endpoint_url='http://localhost:8000', region_name='us-east-1')
        except:
            print 'S3 local connection cannot be established. Please double check your credentials and network connection.'
            return None
        return ddb

    def list_all_tables(self):
        client = boto3.client(AWS_RESOURCE, self.__access_key, self.__secret_key)
        tables = client.list_tables()
        return tables

    #     ddb = self.get_db_connection()
    #     ddb.







