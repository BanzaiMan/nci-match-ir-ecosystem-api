import logging
from accessors.sample_control_accessor import SampleControlAccessor
from flask_restful import abort, Resource, reqparse
from accessors.s3_accessor import S3Accessor


class SampleControlRecordDownloadBamBai(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)


    def get(self, molecular_id, format=None, type=None):
        self.logger.info("Downloading sample control with id: " + str(molecular_id) + ", format: " +
                         str(format) + ", type: " + str(type))
        self.logger.debug("URL passed requested parameters, molecular ids: " + str(molecular_id) + ", format: " +
                          str(format) + ", type: " + str(type))

        try:
            results = SampleControlAccessor().get_item({'molecular_id': molecular_id})

            if 'Item' in results:
                self.logger.debug("Found: " + str(results['Item']))
                # download files from S3 for requested file format
                request_download_file = self.__get_download_file_type(format, type)
                self.logger.info("Requested download file=" + str(request_download_file))

                if request_download_file is not None:
                    s3 = S3Accessor()
                    file_s3_path = results['Item'][request_download_file]
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
                    abort(500, message="No specified file format (vcf|tsv) for downloading")

        except Exception, e:
            self.logger.debug("get_item failed because" + e.message)
            abort(500, message="get_item failed because " + e.message)

        self.logger.info(molecular_id + " was not found")
        abort(404, message=str(molecular_id + " was not found"))


    def __get_download_file_type(self, format, type):

        download_file_type = None
        if 'bam' == format.lower() and 'dna' == type.lower():
            download_file_type = 'dna_bam_name'
        elif 'bam' == format.lower() and 'cdna' == type.lower():
            download_file_type = 'cdna_bam_name'
        elif 'bai' == format.lower() and 'dna' == type.lower():
            download_file_type = 'dna_bai_name'
        elif 'bai' == format.lower() and 'cdna' == type.lower():
            download_file_type = 'cdna_bai_name'
        else:
            self.logger.debug("No valid format(bam|bai) and type(cdna|dna) for downloading.")

        return download_file_type
