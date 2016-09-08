import logging
from accessors.sample_control_accessor import SampleControlAccessor
from flask_restful import abort, Resource
from accessors.s3_accessor import S3Accessor
from resource_helpers.abort_logger import AbortLogger


# TODO: Qing, I found some logic problems and corrected but I haven't tested. Can you test and then make DRY?
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
                s3 = S3Accessor()
                combined_file_format = str(file_format) + "+" + str(nucleic_acid_type)
                request_download_file = s3.get_download_file_type(combined_file_format)
            if request_download_file is None:
                AbortLogger.log_and_abort(500, self.logger.error,
                                          "Requested file format is invalid. Cannot download from S3.")

            self.logger.info("Requested download file format=" + str(request_download_file))
            try:
                s3_url = s3.get_download_url(item[request_download_file])
            except Exception as e:
                AbortLogger.log_and_abort(500, self.logger.error, "Failed to get download url because " + e.message)
            else:
                return {'s3_download_file_url': s3_url}

        AbortLogger.log_and_abort(404, self.logger.debug, str(molecular_id + " was not found"))

