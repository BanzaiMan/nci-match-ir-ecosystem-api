import logging
import boto3
import __builtin__
from flask_restful import Resource
from string import Template

UPLOAD_DIR = Template("$ion_reporter_id/$molecular_id/$analysis_id")
s3Client = boto3.client('s3')
bucket = __builtin__.environment_config[__builtin__.environment]['bucket']

class S3AuthenticationPolicy(Resource):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # Method returns a json with url and fields required to upload to s3

    def get(self, ion_reporter_id, molecular_id, analysis_id, file_name):

        key = UPLOAD_DIR.substitute(ion_reporter_id=ion_reporter_id, molecular_id=molecular_id,
                                    analysis_id=analysis_id)

        key2 = (key + '/' + file_name)
        post = s3Client.generate_presigned_post(Bucket = bucket, Key = key2, ExpiresIn = __builtin__.environment_config
                                                        [__builtin__.environment]['aws_upload_time_limit'])

        return post