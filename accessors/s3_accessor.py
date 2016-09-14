import boto3
import logging
import __builtin__
import json


class S3Accessor(object):

    def __init__(self, region='us-east-1'):
        self.region = region
        self.logger = logging.getLogger(__name__)
        self.resource = boto3.resource('s3')
        self.client = boto3.client('s3', region_name=self.region)
        self.bucket = __builtin__.environment_config[__builtin__.environment]['bucket']
        self.logger.debug("S3Accessor instantiated")

    def upload(self, full_path_local_file, upload_file_location):
        self.logger.info("Attempting to upload: " + full_path_local_file + " to " + upload_file_location)
        try:
            self.resource.meta.client.upload_file(full_path_local_file, self.bucket, upload_file_location)
        except Exception as e:
            self.logger.error("Upload to S3 failed because: " + e.message)
            raise

        self.logger.info("Upload to S3 success!")

    def download(self, s3_path):
        file_base_name = s3_path.rsplit('/', 1)[1]
        full_path_local_file = __builtin__.environment_config[__builtin__.environment]['tmp_file_dir'] +\
                               "/" + file_base_name
        self.logger.info("Attempting to download: " + s3_path + " to " + full_path_local_file)
        try:
            self.resource.meta.client.download_file(self.bucket, s3_path, full_path_local_file)
        except Exception as e:
            self.logger.error("Download from S3 failed because: " + e.message)
            raise

        self.logger.info("Download from S3 success!")
        return full_path_local_file

    # create AWS S3 url for downloading file
    def get_download_url(self, file_s3_path):

        self.logger.info("*********** file_s3_path=" + file_s3_path)
        try:
            s3_url = self.client.generate_presigned_url('get_object',
                                                        Params={'Bucket': self.bucket, 'Key': file_s3_path},
                                                        ExpiresIn=__builtin__.environment_config
                                                        [__builtin__.environment]['aws_download_time_limit'])
        except Exception as e:
            self.logger.error("Failed to create s3 download url because: " + e.message)
            raise
        else:
            return s3_url
