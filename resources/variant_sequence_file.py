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

            if len(item) > 0:
                self.logger.debug("Found: " + str(item))
                # download files from S3 for requested file format
                request_download_file = self.__get_download_file_type(file_format)
                self.logger.info("Requested download file format=" + str(request_download_file))
                s3 = S3Accessor()
                s3_url = s3.get_download_url(item[request_download_file])
                return {'s3_download_file_url': s3_url}
        except Exception as e:
            self.logger.error("get_item failed because " + e.message)
            AbortLogger.log_and_abort(500, self.logger.error, "get_item failed because " + e.message)

        self.logger.info(molecular_id + " was not found")
        AbortLogger.log_and_abort(404, self.logger.error, str(molecular_id + " was not found"))


    def __get_download_file_type(self, format):
        with open("config/s3_download_file_format.json", 'r') as format_file:
            file_format_dict = json.load(format_file)

        download_file_type = None
        if format in file_format_dict:
            download_file_type = file_format_dict[format]
        else:
            self.logger.debug("No file requested to be downloaded from S3.")

        return download_file_type
