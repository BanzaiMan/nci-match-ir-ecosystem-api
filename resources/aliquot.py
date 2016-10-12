import logging
import re
import os
from flask_restful import request, Resource, reqparse
from accessors.sample_control_accessor import SampleControlAccessor
from common.dictionary_helper import DictionaryHelper
from common.patient_ecosystem_connector import PatientEcosystemConnector
from accessors.celery_task_accessor import CeleryTaskAccessor
from resource_helpers.abort_logger import AbortLogger


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
        else:
            # check if molecular_id exists in patient table
            pt_results = PatientEcosystemConnector().verify_molecular_id(molecular_id)
            if len(pt_results) > 0:
                print pt_results
                item = pt_results.copy()
                item.update({'molecular_id_type': 'patient'})
                return item
            else:
                AbortLogger.log_and_abort(404, self.logger.debug, str(molecular_id + " was not found"))

    def put(self, molecular_id):
        self.logger.info("updating molecular_id: " + str(molecular_id))
        args = request.json
        self.logger.debug(str(args))

        if not DictionaryHelper.has_values(args):
            AbortLogger.log_and_abort(400, self.logger.debug, "Need to pass in item updating information in "
                                                              "order to update a sample control item. ")

        self.logger.debug("args has values")

        # check if molecular_id exists in sample_controls table
        molecular_id_type = 'sample_control'
        item = SampleControlAccessor().get_item({'molecular_id': molecular_id})
        if len(item) == 0:
            # check if molecular_id exists in patient table
            pt_results = PatientEcosystemConnector().verify_molecular_id(molecular_id)
            print pt_results
            if len(pt_results) > 0:
                molecular_id_type = 'patient'
            else:
                AbortLogger.log_and_abort(404, self.logger.debug, str(molecular_id + " was not found. Cannot update."))

        item_dictionary = args.copy()
        item_dictionary.update({'molecular_id_type': molecular_id_type})
        distinct_tasks_list = self.__get_distinct_tasks(item_dictionary, molecular_id)
        self.logger.debug("Distinct tasks created")
        tsv_name = None
        if len(distinct_tasks_list) > 0:

            try:
                for distinct_task in distinct_tasks_list:
                    self.logger.debug("Adding task to queue: " + str(distinct_task))
                    # TODO: Remind me why are we doing this?
                    if 'vcf_name' in distinct_task:
                        p = re.compile('.vcf')
                        tsv_name = p.sub('.tsv', distinct_task['vcf_name'])
                        tsv_name = os.path.basename("/" + tsv_name)
                    CeleryTaskAccessor().process_file(distinct_task)
            except Exception as e:
                AbortLogger.log_and_abort(500, self.logger.error, "updated_item failed because" + e.message)
        else:
            AbortLogger.log_and_abort(400, self.logger.debug, "No distinct tasks where found in message")

        if molecular_id_type == 'sample_control':
            return {"message": "Item updated", "molecular_id": molecular_id}
        else:
            # TODO: What happens if vcf_name isn't in message, thus tsv_name is not created?
            return {"ion_reporter_id": item_dictionary['ion_reporter_id'], "molecular_id": molecular_id,
                    "analysis_id": item_dictionary['analysis_id'], "tsv_name": tsv_name}

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

        # TODO: Wny is molecular_id_type and control_type being passed? Not all tasks will have a control type
        tasks_dictionary = {'molecular_id': molecular_id, 'analysis_id': item_dictionary['analysis_id'],
                            'ion_reporter_id': item_dictionary['ion_reporter_id'],
                            'molecular_id_type': item_dictionary['molecular_id_type'],
                            'control_type': item_dictionary['control_type'],
                            file_dict_key: item_dictionary[file_dict_key]}

        if 'site' in item_dictionary:
            tasks_dictionary['site'] = item_dictionary['site']

        return tasks_dictionary
