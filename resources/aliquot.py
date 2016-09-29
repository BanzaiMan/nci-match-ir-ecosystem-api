import logging
from flask_restful import request, Resource, reqparse
from accessors.sample_control_accessor import SampleControlAccessor
from common.dictionary_helper import DictionaryHelper
from accessors.celery_task_accessor import CeleryTaskAccessor
from resource_helpers.abort_logger import AbortLogger


parser = reqparse.RequestParser()
parser.add_argument('analysis_id',   type=str, required=True,  help="'analysis_id' is required")
parser.add_argument('ion_reporter_id', type=str, required=True,  help="'site' is required")
parser.add_argument('dna_bam_name',  type=str, required=False)
parser.add_argument('cdna_bam_name', type=str, required=False)
parser.add_argument('vcf_name',      type=str, required=False)
parser.add_argument('qc_name',       type=str, required=False)


class Aliquot(Resource):
    """This class is for dealing with concepts associated with an aliquot whether it be a sample control or patient.
    Practically, speaking this means when an aliquot has data that needs to be associated with it (like the fact that
    sequence files have been created and loaded to S3, this is the class that handles routing that message to the
    right place"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get(self, molecular_id):
        # 1, Check sample control tables by calling get
        self.logger.info("Checking if molecular id: " + str(molecular_id) + " is in sample control table")
        args = request.args
        self.logger.debug(str(args))
        projection_list, args = DictionaryHelper.get_projection(args)

        results = SampleControlAccessor().get_item({'molecular_id': molecular_id}, ','.join(projection_list))

        if len(results) > 0:
            self.logger.info("Molecular id: " + str(molecular_id) + " found in sample control table")
            item = results.copy()
            item.update({'molecular_id_type': 'sample_control'})
            return item

        # TODO: Finish the write for the GET molecular_id by calling the patient ecosystem
        # 2. Import requests library and then make a rest call to patient ecosystem to check patient table
        AbortLogger.log_and_abort(404, self.logger.debug, str(molecular_id + " was not found"))

    def put(self, molecular_id):
        self.logger.info("updating molecular_id: " + str(molecular_id))
        args = request.json
        self.logger.debug(str(args))

        if not DictionaryHelper.has_values(args):
            AbortLogger.log_and_abort(400, self.logger.debug, "Need to pass in item updating information in "
                                                              "order to update a sample control item. ")

        self.logger.debug("args has values")
        # TODO: before we create messages to tell everyone that the file exist we should just double check that molecular id exist in either the sample control or the patient table. If it doesn't we should return a 404
        item_dictionary = args.copy()
        distinct_tasks_list = self.__get_distinct_tasks(item_dictionary, molecular_id)
        self.logger.debug("Distinct tasks created")
        if len(distinct_tasks_list) > 0:
            try:
                for distinct_task in distinct_tasks_list:
                    self.logger.debug("Adding task to queue: " + str(distinct_task))
                    CeleryTaskAccessor().process_file(distinct_task)
            except Exception as e:
                AbortLogger.log_and_abort(500, self.logger.error, "updated_item failed because" + e.message)
        else:
            AbortLogger.log_and_abort(400, self.logger.debug, "No distinct tasks where found in message")

        return {"message": "Item updated", "molecular_id": molecular_id}

    @staticmethod
    def __get_distinct_tasks(item_dictionary, molecular_id):
        distinct_tasks_list = list()

        if 'vcf_name' in item_dictionary and 'analysis_id' and 'ion_reporter_id' in item_dictionary:
            distinct_tasks_list.append(Aliquot.__get_tasks_dictionary(item_dictionary, molecular_id, 'vcf_name'))

        if 'dna_bam_name' in item_dictionary and 'analysis_id' and 'ion_reporter_id' in item_dictionary:
            distinct_tasks_list.append(Aliquot.__get_tasks_dictionary(item_dictionary, molecular_id, 'dna_bam_name'))

        if 'cdna_bam_name' in item_dictionary and 'analysis_id' and 'ion_reporter_id' in item_dictionary:
            distinct_tasks_list.append(Aliquot.__get_tasks_dictionary(item_dictionary, molecular_id, 'cdna_bam_name'))

        if 'qc_name' in item_dictionary and 'analysis_id' and 'ion_reporter_id' in item_dictionary:
            distinct_tasks_list.append(Aliquot.__get_tasks_dictionary(item_dictionary, molecular_id, 'qc_name'))

        return distinct_tasks_list

    @staticmethod
    def __get_tasks_dictionary(item_dictionary, molecular_id, file_dict_key):

        tasks_dictionary = {'molecular_id': molecular_id, 'analysis_id': item_dictionary['analysis_id'],
                            'ion_reporter_id': item_dictionary['ion_reporter_id'],
                            file_dict_key: item_dictionary[file_dict_key]}

        if 'site' in item_dictionary:
            tasks_dictionary['site'] = item_dictionary['site']

        return tasks_dictionary
