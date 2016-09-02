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


    # TODO: handle zip file if in request 'format=zip'
    # if user only specify molecular_id in request, return sample_controls item of the molecular_id
    # if in request, user specify molecular_id, file (bam, bai, vcf, tsv, or all) and file type (dna, or cdna),
    #    return singed s3 download link of each file
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
                self.logger.info("****** download_file_list=" + str(request_download_filelist))
                if len(request_download_filelist) > 0:
                    s3 = S3Accessor()
                    s3_url_list = []
                    for file_type in request_download_filelist:
                        file_s3_path = results['Item'][file_type]
                        try:
                            s3_url = s3.client.generate_presigned_url('get_object',
                                                                      Params={'Bucket': s3.bucket, 'Key': file_s3_path},
                                                                      ExpiresIn=600)
                        except Exception, e:
                            self.logger.error("Failed to create s3 download url because: " + e.message)
                            raise
                        else:
                            s3_url_list.append(s3_url)
                    return {'s3_download_file_url': s3_url_list}
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
            if args['type'] is not None and 'bam' in args['file'].lower() and 'dna' in args['type'].lower():
                download_file_list.append('dna_bam_name')
            elif args['type'] is not None and 'bam' in args['file'].lower() and 'cdna' in args['type'].lower():
                download_file_list.append('cdna_bam_name')
            elif args['type'] is not None and 'bai' in args['file'].lower() and 'dna' in args['type'].lower():
                download_file_list.append('dna_bai_name')
            elif args['type'] is not None and 'bai' in args['file'].lower() and 'cdna' in args['type'].lower():
                download_file_list.append('cdna_bai_name')
            elif 'bam' in args['file'].lower():
                download_file_list.append('dna_bam_name')
                download_file_list.append('cdna_bam_name')
            elif 'bai' in args['file'].lower():
                download_file_list.append('dna_bai_name')
                download_file_list.append('cdna_bai_name')
            elif 'vcf' in args['file'].lower():
                download_file_list.append('vcf_name')
            elif 'tsv' in args['file'].lower():
                download_file_list.append('tsv_name')
            elif 'all' in args['file'].lower():
                download_file_list.append('dna_bam_name')
                download_file_list.append('dna_bai_name')
                download_file_list.append('cdna_bam_name')
                download_file_list.append('cdna_bai_name')
                download_file_list.append('vcf_name')
                download_file_list.append('tsv_name')
            else:
                self.logger.debug("No file requested to be downloaded from S3.")

        return download_file_list

