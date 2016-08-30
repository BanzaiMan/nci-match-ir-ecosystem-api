import boto3
import os
import json
import logging
from boto3.s3.transfer import TransferConfig
from boto3.s3.transfer import S3Transfer

S3_ALLOWED_EXTENSIONS = {'bam', 'vcf', 'pdf'}
S3_IGNORED_EXTENSIONS = {'bai', 'tsv'}
S3_DOWNLOADABLES = {'bam', 'bai', 'vcf', 'tsv', 'pdf'}


def s3_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in S3_ALLOWED_EXTENSIONS


def s3_ignored_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in S3_IGNORED_EXTENSIONS


def s3_downloadable(file_extension):
    return file_extension in S3_DOWNLOADABLES


class S3Accessor(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("S3Accessor instantiated")

    @staticmethod
    def parse_pedmatch_config():

        pedmatch_conf = '../resources/pedmatch_config.json'
        curr_dir = os.path.dirname(__file__)
        conf_full_path = os.path.join(curr_dir, pedmatch_conf)

        if not os.path.isfile(conf_full_path):
            print 'pedmatch_config.json file is missing!'
        with open(conf_full_path) as config_file:
            config = json.load(config_file)
            return config

    def get_s3_resource(self):
        try:
            s3 = boto3.resource('s3')
            self.logger.info("Checking database for sample_control table existence.")
            print "S3 resource connected."
        except Exception, e:
            self.logger.debug("S3 resource connection failed because: " + e.message)
            print 'S3 resource connection cannot be established. ' + str(e.message)
            return None
        return s3

    # def get_s3_transfer(self):
    #     # multipart_threshold=9999999999999999,  # workaround for 'disable' auto multipart upload
    #     my_config = TransferConfig(
    #         multipart_threshold=8000000,
    #         max_concurrency=10,
    #         num_download_attempts=10,
    #     )
    #
    #     connection = boto3.client(service_name='s3',
    #                               region_name='us-east-1',
    #                               api_version=None,
    #                               use_ssl=True,
    #                               verify=True,
    #                               aws_access_key_id=self.__access_key,
    #                               aws_secret_access_key=self.__secret_key,
    #                               aws_session_token=None,
    #                               config=None)
    #
    #     return S3Transfer(connection, my_config)

    def key_exists(self, bucket_name, key_name):
        s3 = self.get_s3_resource()
        bucket = s3.Bucket(bucket_name)
        objs = list(bucket.objects.filter(Prefix=key_name))
        return len(objs) > 0 and objs[0].key == key_name

    def delete_a_key(self, bucket_name, key_name):
        s3 = self.get_s3_resource()
        bucket = s3.Bucket(bucket_name)
        objs = list(bucket.objects.filter(Prefix=key_name))
        for obj in objs:
            s3.Object(bucket.name, obj.key).delete()

    def get_all_keys(self, bucket_name):
        s3 = self.get_s3_resource()
        bucket = s3.Bucket(bucket_name)
        objs = list(bucket.objects.all())
        keys = []
        for obj in objs:
            keys.append(obj.key)
        return keys

    # def get_all_keys_by_msn(self, bucket_name, alia, msn):
    #     s3 = self.get_s3_resource()
    #     bucket = s3.Bucket(bucket_name)
    #     objs = list(bucket.objects.filter(Prefix=alia+'/'+msn))
    #     keys = []
    #     for obj in objs:
    #         if not obj.key.endswith('/'):#ignore directory key
    #             keys.append(obj.key)
    #     return keys
    #
    # def get_all_keys_by_analysis_id(self, bucket_name, alia, analysis_id):
    #     s3 = self.get_s3_resource()
    #     bucket = s3.Bucket(bucket_name)
    #     objs = list(bucket.objects.filter(Prefix=alia))
    #     keys = []
    #     for obj in objs:
    #         if not obj.key.endswith('/') and analysis_id in obj.key:#ignore directory key
    #             keys.append(obj.key)
    #     return keys

    def bucket_exists(self, bucket_name):
        s3 = self.get_s3_resource()
        return s3.Bucket(bucket_name) in s3.buckets.all()




