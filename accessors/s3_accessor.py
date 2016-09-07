import boto3
import logging
import __builtin__


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
