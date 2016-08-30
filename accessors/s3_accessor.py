import boto3
import logging
import __builtin__


class S3Accessor(object):

    def __init__(self, region='us-east-1'):
        self.region = region
        self.logger = logging.getLogger(__name__)
        self.logger.debug("S3Accessor instantiated")
        self.resource = boto3.resource('s3')
        self.client = boto3.client('s3', region_name=self.region)
        self.bucket = __builtin__.environment_config[__builtin__.environment]['bucket']

    def upload(self, full_path_local_file, upload_file_location):
        self.logger.info("Attempting to upload: " + full_path_local_file + " to " + upload_file_location)
        try:
            self.resource.meta.client.upload_file(full_path_local_file, self.bucket, upload_file_location)
        except Exception, e:
            self.logger.error("Upload to S3 failed because: " + e.message)
            raise

        self.logger.info("Upload to S3 success!")

    def download(self, s3_path):
        pass
