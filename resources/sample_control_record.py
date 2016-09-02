import logging
from accessors.celery_task_accessor import CeleryTaskAccessor
from accessors.sample_control_accessor import SampleControlAccessor
from flask_restful import abort, Resource, reqparse
from flask import request
from common.dictionary_helper import DictionaryHelper
from accessors.s3_accessor import S3Accessor

parser = reqparse.RequestParser()
# Essential for POST, all other parameters are ignored on post except molecular_id, which, if passed in will cause a
# failure. The proper order is to first POST to get a molecular_id then to PUT the files using the molecular_id in the
# URI. From there other fields can be updated if needed.
parser.add_argument('format',       type=str, required=False)  # format=zip
parser.add_argument('file',         type=str, required=False)  # file=bam|bai|vcf|tsv|all
parser.add_argument('type',         type=str, required=False)  # type=cdna|dna


class SampleControlRecord(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # this put should just put items on the queue through celery and then let celery update
    # the database, shouldn't process files (molecular_id resource does that).
    # This is just straight updates of attributes.
    def put(self, molecular_id):
        self.logger.info("updating sample control with id: " + str(molecular_id))
        args = request.json
        self.logger.debug(str(args))

        if not DictionaryHelper.has_values(args):
            self.logger.debug("Update item failed, because data to update item with was not passed in request")
            abort(400, message="Update item failed, because data to update item with was not passed in request")

        item_dictionary = args.copy()
        item_dictionary.update({'molecular_id': molecular_id})

        # Very important line of code this takes all of the 'None' values out of the dictionary.
        # Without this, the record would update all attributes in the params above with 'None' unless they
        # were explicitly passed in. In reality, we only want to update the attributes that have been explicitly
        # passed in from the params. If they haven't been passed in then they shouldn't be updated.
        item_dictionary = dict((k, v) for k, v in item_dictionary.iteritems() if v)
        try:
            CeleryTaskAccessor().update_item(item_dictionary)
        except Exception, e:
            self.logger.debug("updated_item failed because " + e.message)
            abort(500, message="Update item failed, because " + e.message)

        return {"message": "Sample control with molecular id: " + molecular_id + " updated"}

    def delete(self, molecular_id):
        self.logger.info("Deleting sample control with id: " + str(molecular_id))
        try:
            CeleryTaskAccessor().delete_item({'molecular_id': molecular_id})
            return {"message": "Item deleted", "molecular_id": molecular_id}
        except Exception, e:
            self.logger.debug("delete_item failed because" + e.message)
            abort(500, message="delete_item item failed, because " + e.message)

    # TODO: Expand GET functionality to zip downloaded s3 files and test.
    # TODO: Confirm if new return dictionary is ok.
    def get(self, molecular_id):
        self.logger.info("Getting sample control with id: " + str(molecular_id))
        args = parser.parse_args()
        self.logger.debug("URL passed requested arguments: " + str(args))

        try:
            results = SampleControlAccessor().get_item({'molecular_id': molecular_id})

            if 'Item' in results:
                self.logger.debug("Found: " + str(results['Item']))

                # download files from S3, if requested
                request_download_filelist = self.__get_download_file_list(args)
                self.logger.debug("Download s3 file list=" + str(request_download_filelist))
                if len(request_download_filelist) > 0:
                    downloaded_filelist = []
                    for file_type in request_download_filelist:
                        file_s3_path = results['Item'][file_type]
                        try:
                            downloaded_file_path = S3Accessor().download(file_s3_path)
                        except Exception, e:
                            self.logger.error("Failed to download s3 file because: " + e.message)
                            raise
                        else:
                            downloaded_filelist.append(downloaded_file_path)
                    return {'item': results['Item'], 'downloaded_files': downloaded_filelist}
                else:
                    return results['Item']

        except Exception, e:
            self.logger.debug("get_item failed because" + e.message)
            abort(500, message="get_item failed because " + e.message)

        self.logger.info(molecular_id + " was not found")
        abort(404, message=str(molecular_id + " was not found"))

    def __get_download_file_list(self, args):
        download_file_list = []

        if DictionaryHelper.has_values(args):
            if args['file'] == 'bam' and args['type'] == 'dna':
                download_file_list.append('dna_bam_name')
            elif args['file'] == 'bam' and args['type'] == 'cdna':
                download_file_list.append('cdna_bam_name')
            elif args['file'] == 'bai' and args['type'] == 'dna':
                download_file_list.append('dna_bai_name')
            elif args['file'] == 'bai' and args['type'] == 'cdna':
                download_file_list.append('cdna_bai_name')
            elif args['file'] == 'bam':
                download_file_list.append('dna_bam_name')
                download_file_list.append('cdna_bam_name')
            elif args['file'] == 'bai':
                download_file_list.append('dna_bai_name')
                download_file_list.append('cdna_bai_name')
            elif args['file'] == 'vcf':
                download_file_list.append('vcf_name')
            elif args['file'] == 'tsv':
                download_file_list.append('tsv_name')
            elif args['file'] == 'all':
                download_file_list.append('dna_bam_name')
                download_file_list.append('dna_bai_name')
                download_file_list.append('cdna_bam_name')
                download_file_list.append('cdna_bai_name')
                download_file_list.append('vcf_name')
                download_file_list.append('tsv_name')
            else:
                self.logger.debug("No file requested to be downloaded from S3.")

        return download_file_list