import logging
import boto3
import __builtin__
import json
import requests
import botocore
from flask_restful import Resource, request
from string import Template
from resources.aliquot import Aliquot
from resource_helpers.abort_logger import AbortLogger

UPLOAD_DIR = Template("$ion_reporter_id/$molecular_id/$analysis_id")
s3Client = boto3.client('s3')
s3_resource = boto3.resource('s3')
bucket = __builtin__.environment_config[__builtin__.environment]['bucket']
bucket2 = s3_resource.Bucket(bucket)


class S3AuthenticationPolicy(Resource):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # Method returns url for file upload
    # @cross_origin(headers=['Content-Type', 'Authorization'])
    # @requires_auth
    def get(self, ion_reporter_id, molecular_id, analysis_id, file_name):

        response = Aliquot()
        item = response.get(molecular_id)
        results = json.loads(item.data)
        key = UPLOAD_DIR.substitute(ion_reporter_id=ion_reporter_id, molecular_id=molecular_id,
                                   analysis_id=analysis_id)
        key2 = (key + '/' + file_name)
        objs = list(bucket2.objects.filter(Prefix=key2))

        if len(objs) > 0 and objs[0].key == key2:
            AbortLogger.log_and_abort(409, self.logger.debug,
                                      str("Cannot upload to s3 location, file already exists."))

        if results['molecular_id_type'] == 'sample_control':
            try:
                post = s3Client.generate_presigned_post(Bucket=bucket,
                                                        Key=key2,
                                                        ExpiresIn=
                                                        __builtin__.environment_config[__builtin__.environment]
                                                        ['aws_upload_time_limit'])
                return post
            except Exception as e:
                    AbortLogger.log_and_abort(503, self.logger.debug,
                                              str(" s3Client failed to generate presigned post." + e.message))
        elif results['molecular_id_type'] == 'patient':
            # TODO: Change to status when parameter is created

            if results['uuid'] == 0:
                try:
                    post = s3Client.generate_presigned_post(Bucket=bucket,
                                                            Key=key2,
                                                            ExpiresIn=
                                                            __builtin__.environment_config[__builtin__.environment]
                                                            ['aws_upload_time_limit'])
                    return post
                except Exception as e:
                    AbortLogger.log_and_abort(503, self.logger.debug,
                                              str(" s3Client failed to generate presigned post." + e.message))
            else:
                # TODO: Change to status when parameter is created
                AbortLogger.log_and_abort(409, self.logger.debug,
                                          str("Cannot upload, patient variant report status: " + results['uuid']))

        else:
            AbortLogger.log_and_abort(500, self.logger.debug,
                                      str("Invalid molecular_id_type; contact help."))


