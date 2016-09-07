import logging
from accessors.sample_control_accessor import SampleControlAccessor
from flask_restful import abort, Resource
from accessors.s3_accessor import S3Accessor


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
            results = SampleControlAccessor().get_item({'molecular_id': molecular_id})

            if len(results) > 0:
                self.logger.debug("Found: " + str(results))
                # download files from S3 for requested file format
                request_download_file = self.__get_download_file_type(file_format)
                self.logger.info("Requested download file=" + str(request_download_file))
                if request_download_file is not None:
                    # TODO: I think this should likely be encapsulated and completely hidden from this module
                    # TODO: Put the expires in time in environment.yml
                    s3 = S3Accessor()
                    file_s3_path = results[request_download_file]
                    try:
                        s3_url = s3.client.generate_presigned_url('get_object',
                                                                  Params={'Bucket': s3.bucket, 'Key': file_s3_path},
                                                                  ExpiresIn=600)
                    except Exception, e:
                        self.logger.error("Failed to create s3 download url because: " + e.message)
                        abort(500, message="Failed to create s3 download url because: " + e.message)
                    else:
                        return {'s3_download_file_url': s3_url}
                else:
                    self.logger.debug("No specified file format (vcf|tsv) for downloading")
                    abort(404, message="No specified file format (vcf|tsv) for downloading")

        except Exception, e:
            self.logger.error("get_item failed because" + e.message)
            abort(500, message="get_item failed because " + e.message)

        self.logger.info(molecular_id + " was not found")
        abort(404, message=str(molecular_id + " was not found"))

    # TODO: Could simplify into 2 lines of code with a dictionary I think
    def __get_download_file_type(self, format):

        download_file_type = None
        if 'vcf' == format.lower():
            download_file_type = 'vcf_name'
        elif 'tsv' == format.lower():
            download_file_type = 'tsv_name'
        else:
            self.logger.debug("No file requested to be downloaded from S3.")

        return download_file_type
