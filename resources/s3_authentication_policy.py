import logging
import hmac
import hashlib
import os
import __builtin__
from flask_restful import Resource
from base64 import b64encode
from datetime import datetime, timedelta
from json import dumps
from string import Template
from accessors.sample_control_accessor import SampleControlAccessor
from resource_helpers.abort_logger import AbortLogger

UPLOAD_DIR = Template("$site/$molecular_id/$analysis_id")


class S3AuthenticationPolicy(Resource):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get(self, molecular_id, analysis_id, file_name):

        key = UPLOAD_DIR.substitute(site=self.__get_site(molecular_id), molecular_id=molecular_id,
                                    analysis_id=analysis_id)

        policy = self.__make_policy(key)
        return {
            "policy": policy,
            "signature": self.__sign_policy(policy),
            "key": key + "/" + file_name,
            "success_action_redirect": "/"
        }

    # Method creates encrypted policy signature
    @staticmethod
    def __sign_policy(policy):
        return b64encode(hmac.new(os.environ['AWS_SECRET_ACCESS_KEY'], policy, hashlib.sha256).digest())

    # method builds JSON policy according to AWS standards
    @staticmethod
    def __make_policy(key):
        policy_object = {
            "expiration": (datetime.now() + timedelta(
                hours= __builtin__.environment_config[__builtin__.environment]['s3_auth_policy_exp'])).strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            "conditions": [
                {"bucket": __builtin__.environment_config[__builtin__.environment]['bucket']},
                {"acl": "public-read"},
                ["starts-with", "$key", key],
                {"success_action_status": "201"}
            ]
        }
        return b64encode(dumps(policy_object).replace('\n', '').replace('\r', ''))

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

