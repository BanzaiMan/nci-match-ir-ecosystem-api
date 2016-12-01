import logging
import boto3
import __builtin__
from flask_restful import Resource
from string import Template
from accessors.sample_control_accessor import SampleControlAccessor
from resource_helpers.abort_logger import AbortLogger

UPLOAD_DIR = Template("$site/$molecular_id/$analysis_id")
s3Client = boto3.client('s3')
bucket = __builtin__.environment_config[__builtin__.environment]['bucket']

class S3AuthenticationPolicy(Resource):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get(self, molecular_id, analysis_id, file_name):

        key = UPLOAD_DIR.substitute(site=self.__get_site(molecular_id), molecular_id=molecular_id,
                                    analysis_id=analysis_id)

        expiration = __builtin__.environment_config[__builtin__.environment]['s3_auth_policy_exp']
        key2 = (key + '/' + file_name)
        url = s3Client.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': key2}, ExpiresIn=expiration)

        return {
            'key': key,
            "url": url
        }

    def post(self, molecular_id, analysis_id, file_name):

        key = UPLOAD_DIR.substitute(site=self.__get_site(molecular_id), molecular_id=molecular_id,
                                    analysis_id=analysis_id)

        key2 = (key + '/' + file_name)
        post = s3Client.generate_presigned_post(Bucket = bucket, Key = key2)

        return post


    # Method simply queries database based on molecular_id to find the site that is authorized to use the molecular_id
    def __get_site(self, molecular_id):
        try:
            results = SampleControlAccessor().scan({'molecular_id': molecular_id}, '')
        except Exception as e:
            AbortLogger.log_and_abort(500, self.logger.error, "Get failed because: " + e.message)
        else:
            if len(results) > 0:
                if 'site' in results[0]:
                    return results[0]['site']
                else:
                    AbortLogger.log_and_abort(500, self.logger.error,
                                              "Get failed because molecular id was found but there was no "
                                              "site associated with it. Contact support.")
            else:
                # TODO: Query Patient ecosystem
                AbortLogger.log_and_abort(501, self.logger.error,
                                          "Molecular id was not found in sample control table and searching "
                                          "patient table is not yet implemented")

