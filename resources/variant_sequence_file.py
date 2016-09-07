import logging
import json
from accessors.sample_control_accessor import SampleControlAccessor
from flask_restful import abort, Resource
from accessors.s3_accessor import S3Accessor
from resource_helpers.abort_logger import AbortLogger


class VariantSequenceFile(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # if in request, user specify molecular_id, file format(bam, bai, vcf, tsv) and file type (dna, or cdna),
    #    return singed s3 download link of each file
    def get(self, molecular_id, file_format):
        self.logger.info("Downloading sample control with id: " + str(molecular_id) + ", format: " +
                         str(file_format))
        self.logger.debug("URL passed requested parameters, molecular ids: " + str(molecular_id) + ", format: " +
                          str(file_format))

        try:
            item = SampleControlAccessor().get_item({'molecular_id': molecular_id})
        except Exception as e:
            AbortLogger.log_and_abort(500, self.logger.error, "get_item failed because " + e.message)
        else:
            if len(item) > 0:
                self.logger.debug("Found: " + str(item))
                # TODO: Qing, I think there is a bug here as the else is not dealt with
                request_download_file = self.__get_download_file_type(file_format)
                self.logger.info("Requested download file format=" + str(request_download_file))
                try:
                    s3_url = S3Accessor().get_download_url(item[request_download_file])
                except Exception as e:
                    AbortLogger.log_and_abort(500, self.logger.error, "get_item failed because " + e.message)
                else:
                    return {'s3_download_file_url': s3_url}

            AbortLogger.log_and_abort(404, self.logger.debug, str(molecular_id + " was not found"))

    def __get_download_file_type(self, file_format):
        with open("config/s3_download_file_format.json", 'r') as format_file:
            file_format_dict = json.load(format_file)

        download_file_type = None
        if file_format in file_format_dict:
            download_file_type = file_format_dict[file_format]
        else:
            self.logger.debug("No file requested to be downloaded from S3.")

        return download_file_type
