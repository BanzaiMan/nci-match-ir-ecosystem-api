import logging
import os.path
import sys
import re

from werkzeug.utils import secure_filename
from accessors.s3_accessor import S3Accessor

class S3Uploader(object):

    ## this item_dictionary is updated dictionary, need have molecular_id, site, analysis_id, file_full_path
    def __init__(self, bucket, upload_item_dictionary):
        self.logger = logging.getLogger(__name__)
        self.s3_accessor = S3Accessor()
        self.bucket = bucket
        self.site = upload_item_dictionary['site']
        self.molecular_id = upload_item_dictionary['molecular_id']
        self.analysis_id = upload_item_dictionary['analysis_id']
        if 'vcf_name' in upload_item_dictionary:
            self.file_full_path = upload_item_dictionary['vcf_name']
        elif 'dna_bam_name' in upload_item_dictionary:
            self.file_full_path = upload_item_dictionary['dna_bam_name']
        elif 'cdna_bam_name' in upload_item_dictionary:
            self.file_full_path = upload_item_dictionary['cdna_bam_name']

    def create_s3_path(self):
        file_full_path = self.file_full_path
        if file_full_path.endswith("pdf"):
            file_base_name = secure_filename(file_full_path.split("QC/")[1])
        else:
            file_base_name = secure_filename(os.path.basename(file_full_path))

        s3_path = self.site + "/" + self.molecular_id + "/" + self.analysis_id + "/" + file_base_name
        return s3_path

    def upload_file(self):
        s3_resource = self.s3_accessor.get_s3_resource()
        file_full_path = self.file_full_path
        s3_path = self.create_s3_path()

        # upload file to s3, if file exists in s3, will overwrite
        try:
            s3_resource.meta.client.upload_file(file_full_path, self.bucket, s3_path)
            print "Upload to S3 success! uploaded file s3 path = " + s3_path + "\n"
            self.logger.info("Upload success! uploaded file s3 path = " + str(s3_path))
            # return {"message": "Uploaded to S3", "file_s3_path": s3_path}
            return s3_path
        except Exception, e:
            print "Failed to upload to S3 for file: " + file_full_path + "\n"
            self.logger.debug("Upload to S3 failed for file: " + file_full_path + e.message)
            self.logger.debug("Failure reason: " + e.message)
            return None

