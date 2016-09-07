import logging
from accessors.sample_control_accessor import SampleControlAccessor
from flask_restful import abort, Resource
from accessors.s3_accessor import S3Accessor


# TODO: Qing, I found some logic problems and corrected but I haven't tested. Can you test and then make DRY?
class AlignmentSequenceFile(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get(self, molecular_id, file_format, nucleic_acid_type):
        self.logger.debug("URL passed requested parameters, molecular ids: " + str(molecular_id) + ", format: " +
                          str(file_format) + ", type: " + str(nucleic_acid_type))

        try:
            results = SampleControlAccessor().get_item({'molecular_id': molecular_id})
        except Exception, e:
            self.logger.debug("get_item failed because" + e.message)
            abort(500, message="get_item failed because " + e.message)
        else:
            if len(results) > 0:
                self.logger.debug("Found: " + str(results))
                # download files from S3 for requested file format
                request_download_file = self.__get_download_file_type(file_format, nucleic_acid_type)
                self.logger.info("Requested download file=" + str(request_download_file))

                if request_download_file is not None:
                    # TODO: I think this should likely be encapsulated and completely hidden from this module
                    # TODO: Put the expires in time in environment.yml
                    # TODO: Notice also how this code is identical to the code in the Variant Sequence File class.
                    s3 = S3Accessor()
                    file_s3_path = results[request_download_file] if request_download_file in results else None
                    if file_s3_path is not None:
                        try:
                            s3_url = s3.client.generate_presigned_url('get_object',
                                                                      Params={'Bucket': s3.bucket, 'Key': file_s3_path},
                                                                      ExpiresIn=600)
                        except Exception, e:
                            self.logger.error("Failed to create s3 download url because: " + e.message)
                            abort(500, message="Failed to create s3 download url because: " + e.message)
                        else:
                            return {'s3_download_file_url': s3_url}

                self.logger.debug("No specified file format (vcf|tsv) for downloading")
                abort(404, message="No specified file format (vcf|tsv) for downloading")

            self.logger.info(molecular_id + " was not found")
            abort(404, message=str(molecular_id + " was not found"))

    # TODO: Could simplify into 2 lines of code with a dictionary I think
    def __get_download_file_type(self, file_format, nucleic_acid_type):

        download_file_type = None
        if 'bam' == file_format.lower() and 'dna' == nucleic_acid_type.lower():
            download_file_type = 'dna_bam_name'
        elif 'bam' == file_format.lower() and 'cdna' == nucleic_acid_type.lower():
            download_file_type = 'cdna_bam_name'
        elif 'bai' == file_format.lower() and 'dna' == nucleic_acid_type.lower():
            download_file_type = 'dna_bai_name'
        elif 'bai' == file_format.lower() and 'cdna' == nucleic_acid_type.lower():
            download_file_type = 'cdna_bai_name'
        else:
            self.logger.debug("No valid format(bam|bai) and type(cdna|dna) for downloading.")

        return download_file_type
