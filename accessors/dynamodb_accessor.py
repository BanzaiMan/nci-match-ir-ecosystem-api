import boto3
import os
import json
import socket
import zipfile

from boto3.dynamodb.conditions import Key

AWS_RESOURCE = 'dynamodb'





class DynamoDBAccessor(object):

    def __init__(self):
        self.__access_key, self.__secret_key, self.__region_name = DynamoDBAccessor.aws_credentials()

    @staticmethod
    def aws_credentials():
        if socket.gethostname() == 'NCI-01967369-ML':#local machine for dev
            return os.environ['AWS_ACCESS_KEY_ID'], os.environ['AWS_SECRET_ACCESS_KEY'], 'us-west-2'
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

    def list_all_tables_local(self):
        client = boto3.client(AWS_RESOURCE,
                              endpoint_url='http://localhost:8000',
                              region_name='us-west-2')
        tables = client.list_tables()
        print tables
        return tables

if __name__ == '__main__':
    tst_accessor = DynamoDBAccessor()
    #print tst_accessor.get_new_molecular_id('MoCha')
    #print tst_accessor.get_new_molecular_id('MDACC')
    print tst_accessor.list_all_tables_local()







