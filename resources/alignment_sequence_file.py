import logging
import __builtin__
from accessors.sample_control_accessor import SampleControlAccessor
from flask_restful import Resource
from accessors.s3_accessor import S3Accessor
from resource_helpers.abort_logger import AbortLogger


class AlignmentSequenceFile(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get(self, molecular_id, file_format, nucleic_acid_type):
        self.logger.debug("URL passed requested parameters, molecular ids: " + str(molecular_id) + ", format: " +
                          str(file_format) + ", type: " + str(nucleic_acid_type))
        try:
            item = SampleControlAccessor().get_item({'molecular_id': molecular_id})
        except Exception as e:
            AbortLogger.log_and_abort(500, self.logger.error, "get_item failed because " + e.message)
        else:
            if len(item) > 0:
                self.logger.debug("Found: " + str(item))
                try:
                    s3_url = S3Accessor(__builtin__.environment_config[__builtin__.environment]['region'])\
                        .get_download_url(item[str(nucleic_acid_type) + "_" + str(file_format) + "_name"])
                except KeyError as k:
                    AbortLogger.log_and_abort(404, self.logger.debug, "Failed to get download url because " +
                                              k.message + " does not exist")
                except Exception as e:
                    AbortLogger.log_and_abort(500, self.logger.error, "Failed to get download url because " + e.message)
                else:
                    return {'s3_download_file_url': s3_url}

        AbortLogger.log_and_abort(404, self.logger.debug, str(molecular_id + " was not found"))
