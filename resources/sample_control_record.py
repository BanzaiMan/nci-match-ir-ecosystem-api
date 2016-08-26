import logging
from accessors.celery_task_accessor import CeleryTaskAccessor
from accessors.sample_control_accessor import SampleControlAccessor
from flask_restful import abort, request, reqparse, Resource
from common.dictionary_helper import DictionaryHelper


parser = reqparse.RequestParser()
parser.add_argument('analysis_id',   type=str, required=False, location='json')
parser.add_argument('dna_bam_path',  type=str, required=False, location='json')
parser.add_argument('cdna_bam_path', type=str, required=False, location='json')
parser.add_argument('vcf_path',      type=str, required=False, location='json')


class SampleControlRecord(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def put(self, molecular_id):
        self.logger.info("updating sample control with id: " + str(molecular_id))
        args = parser.parse_args()
        self.logger.debug(str(args))

        if not DictionaryHelper.has_values(args):
            self.logger.debug("update item failed, because item updating information was not passed in request")
            abort(400, message="Need passing item updating information in order to update a sample control item. ")

        item_dictionary = args.copy()
        item_dictionary.update({'molecular_id': molecular_id})

        try:
            CeleryTaskAccessor().vcf_item(item_dictionary)
            # SampleControlAccessor().update(item_dictionary)
            return {"message": "Item updated", "molecular_id": molecular_id}
        except Exception, e:
            self.logger.debug("updated_item failed because" + e.message)

    def delete(self, molecular_id):
        self.logger.info("Deleting sample control with id: " + str(molecular_id))
        try:
            # TODO: Instead of writing directly put on queue and then pop off queue to do delete
            SampleControlAccessor().delete_item({'molecular_id': molecular_id})
            return {"message": "Item deleted", "molecular_id": molecular_id}
        except Exception, e:
            self.logger.debug("delete_item failed because" + e.message)

    def get(self, molecular_id):
        self.logger.info("Getting sample control with id: " + str(molecular_id))
        try:
            results = SampleControlAccessor().get_item({'molecular_id': molecular_id})

            if 'Item' in results:
                self.logger.debug("Found: " + str(results['Item']))
                return results['Item']

        except Exception, e:
            self.logger.debug("get_item failed because" + e.message)
            abort(500, message="get_item failed because " + e.message)

        self.logger.info(molecular_id + " was not found")
        abort(404, message=str(molecular_id + " was not found"))
