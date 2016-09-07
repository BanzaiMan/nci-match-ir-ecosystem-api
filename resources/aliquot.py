import logging
from flask_restful import abort, reqparse, Resource
from accessors.sample_control_accessor import SampleControlAccessor
from common.dictionary_helper import DictionaryHelper
from accessors.celery_task_accessor import CeleryTaskAccessor

parser = reqparse.RequestParser()
parser.add_argument('analysis_id',   type=str, required=True,  location='json', help="'analysis_id' is required")
parser.add_argument('site',          type=str, required=True,  location='json', help="'site' is required")
parser.add_argument('dna_bam_name',  type=str, required=False, location='json')
parser.add_argument('cdna_bam_name', type=str, required=False, location='json')
parser.add_argument('vcf_name',      type=str, required=False, location='json')
parser.add_argument('qc_name',       type=str, required=False, location='json')


class Aliquot(Resource):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get(self, molecular_id):
        # 1, Check sample control tables by calling get
        self.logger.info("Checking if molecular id: " + str(molecular_id) + " is in sample control table")
        results = SampleControlAccessor().get_item({'molecular_id': molecular_id})

        if len(results) > 0 :
            self.logger.info("Molecular id: " + str(molecular_id) + " found in sample control table")
            item = results.copy()
            item.update({'molecular_id_type': 'sample_control'})
            return item

        # TODO: Finish the write for the GET molecular_id by calling the patient ecosystem
        # 2. Import requests library and then make a rest call to patient ecosystem to check patient table

        abort(404, message=str(molecular_id + " was not found"))

    def put(self, molecular_id):
        self.logger.info("updating molecular_id: " + str(molecular_id))
        args = parser.parse_args()
        self.logger.debug(str(args))

        if not DictionaryHelper.has_values(args):
            self.logger.debug("update item failed, because item updating information was not passed in request")
            abort(400, message="Need passing item updating information in order to update a sample control item. ")

        item_dictionary = args.copy()
        distinct_tasks_list = self.__get_distinct_tasks(item_dictionary, molecular_id)

        if len(distinct_tasks_list) > 0:
            try:
                for distinct_task in distinct_tasks_list:
                    self.logger.debug("Adding task to queue: " + str(distinct_task))
                    CeleryTaskAccessor().process_file(distinct_task)
            except Exception, e:
                self.logger.debug("updated_item failed because" + e.message)
                abort(500, message="Updating_item failed because: " + e.message)
        else:
            self.logger.debug("No distinct tasks where found in message")
            abort(404, message="No distinct tasks where found in message")

        return {"message": "Item updated", "molecular_id": molecular_id}

    @staticmethod
    def __get_distinct_tasks(item_dictionary, molecular_id):
        distinct_tasks_list = list()

        if 'vcf_name' in item_dictionary and 'analysis_id' and 'site' in item_dictionary:
            distinct_tasks_list.append(Aliquot.__get_tasks_dictionary(item_dictionary, molecular_id, 'vcf_name'))

        if 'dna_bam_name' in item_dictionary and 'analysis_id' and 'site' in item_dictionary:
            distinct_tasks_list.append(Aliquot.__get_tasks_dictionary(item_dictionary, molecular_id, 'dna_bam_name'))

        if 'cdna_bam_name' in item_dictionary and 'analysis_id' and 'site' in item_dictionary:
            distinct_tasks_list.append(Aliquot.__get_tasks_dictionary(item_dictionary, molecular_id, 'cdna_bam_name'))

        if 'qc_name' in item_dictionary and 'analysis_id' and 'site' in item_dictionary:
            distinct_tasks_list.append(Aliquot.__get_tasks_dictionary(item_dictionary, molecular_id, 'qc_name'))

        return distinct_tasks_list

    @staticmethod
    def __get_tasks_dictionary(item_dictionary, molecular_id, file_dict_key):
        return {'site': item_dictionary['site'],
                'molecular_id': molecular_id,
                'analysis_id': item_dictionary['analysis_id'],
                file_dict_key: item_dictionary[file_dict_key]}

