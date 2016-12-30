import logging
import json
import simplejson
from flask_restful import request, Resource, reqparse
from accessors.sample_control_accessor import SampleControlAccessor
from common.dictionary_helper import DictionaryHelper
from common.patient_ecosystem_connector import PatientEcosystemConnector
from accessors.celery_task_accessor import CeleryTaskAccessor
from resource_helpers.abort_logger import AbortLogger
from flask.ext.cors import cross_origin
from resources.auth0_resource import requires_auth
from flask.json import jsonify


class Aliquot(Resource):
    """This class is for dealing with concepts associated with an aliquot whether it be a sample control or patient.
    Practically, speaking this means when an aliquot has data that needs to be associated with it (like the fact that
    sequence files have been created and loaded to S3, this is the class that handles routing that message to the
    right place"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @cross_origin(headers=['Content-Type', 'Authorization'])
    @requires_auth
    def get(self, molecular_id):
        # check if molecular_id exists in sample control table
        self.logger.info("Checking if molecular id: " + str(molecular_id) + " is in sample control table")
        args = request.args
        auth_token = request.headers.get('authorization')
        auth_token = auth_token[7:]
        self.logger.debug(str(args))
        projection_list, args = DictionaryHelper.get_projection(args)

        try:
            results = SampleControlAccessor().get_item({'molecular_id': molecular_id}, ','.join(projection_list))
        except Exception as e:

            AbortLogger.log_and_abort(500, self.logger.error,
                                      "Failed to get " + molecular_id + ", because : " + e.message)

        # results = SampleControlAccessor().get_item({'molecular_id': molecular_id}, ','.join(projection_list))

        if len(results) > 0:
            self.logger.info("Molecular id: " + str(molecular_id) + " found in sample control table")
            results = json.loads(simplejson.dumps(results, use_decimal=True))
            item = results.copy()
            item.update({"molecular_id_type": "sample_control"})
            return jsonify(item)
        else:
            # check if molecular_id exists in patient table
            self.logger.info("Checking if molecular id: " + str(molecular_id) + " is in patient table")
            try:
                (pt_statuscode, pt_data) = PatientEcosystemConnector().verify_molecular_id(molecular_id, auth_token)
            except Exception as e:
                AbortLogger.log_and_abort(503, self.logger.error,
                                          "Failed to reach patient ecosystem to get " + molecular_id + ", because : " + str(e.message))
            # (pt_statuscode, pt_data) = PatientEcosystemConnector().verify_molecular_id(molecular_id)
            if pt_statuscode == 200:
                item = pt_data.copy()
                item.update({"molecular_id_type": "patient"})
                return jsonify(item)
            else:
                self.logger.error("Molecular id: " + str(molecular_id) + " was not found in sample control table or patient ecosystem; PTeco returned: " + str(pt_statuscode))
                AbortLogger.log_and_abort(pt_statuscode, self.logger.debug, str(
                    molecular_id + " was not found. Invalid molecular_id or invalid projection key entered. Status code: " + str(pt_statuscode)))

    @cross_origin(headers=['Content-Type', 'Authorization'])
    @requires_auth
    def put(self, molecular_id):
        self.logger.info("updating molecular_id: " + str(molecular_id))
        args = request.json
        auth_token = request.headers.get('authorization')
        auth_token = auth_token[7:]
        self.logger.debug(str(args))

        if not DictionaryHelper.has_values(args):
            AbortLogger.log_and_abort(400, self.logger.debug, "Need to pass in item updating information in "
                                                              "order to update a sample control item. ")

        self.logger.debug("args has values")

        # check if molecular_id exists in sample_controls table
        try:
            item = SampleControlAccessor().get_item({'molecular_id': molecular_id})
        except Exception as e:
            AbortLogger.log_and_abort(500, self.logger.error,
                                      "Failed to get " + molecular_id + ", because : " + str(e.message))
        # item = SampleControlAccessor().get_item({'molecular_id': molecular_id})
        if len(item) == 0:
            # check if molecular_id exists in patient table
            try:
                (pt_statuscode, pt_data) = PatientEcosystemConnector().verify_molecular_id(molecular_id, auth_token)
            except Exception as e:
                AbortLogger.log_and_abort(503, self.logger.error,
                                          "Failed to reach patient ecosystem to get " + molecular_id + ", because : " + str(
                                              e.message))
            # (pt_statuscode, pt_data) = PatientEcosystemConnector().verify_molecular_id(molecular_id)

            if pt_statuscode != 200:
                AbortLogger.log_and_abort(404, self.logger.debug, str(molecular_id + " was not found. Cannot update."))

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

        return jsonify({"message": "Item updated", "molecular_id": molecular_id})

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

        if 'confirmed' in item_dictionary and 'analysis_id' and 'ion_reporter_id' in item_dictionary:
            distinct_tasks_list.append(Aliquot.__get_tasks_dictionary(item_dictionary, molecular_id, 'confirmed'))

        if 'report_status' in item_dictionary and 'analysis_id' and 'ion_reporter_id' in item_dictionary:
            distinct_tasks_list.append(Aliquot.__get_tasks_dictionary(item_dictionary, molecular_id, 'report_status'))

        if 'comments' in item_dictionary and 'analysis_id' and 'ion_reporter_id' in item_dictionary:
            distinct_tasks_list.append(Aliquot.__get_tasks_dictionary(item_dictionary, molecular_id, 'comments'))

        return distinct_tasks_list

    @staticmethod
    def __get_tasks_dictionary(item_dictionary, molecular_id, file_dict_key):

        tasks_dictionary = {'molecular_id': molecular_id, 'analysis_id': item_dictionary['analysis_id'],
                            'ion_reporter_id': item_dictionary['ion_reporter_id'],
                            file_dict_key: item_dictionary[file_dict_key]}

        if 'site' in item_dictionary:
            tasks_dictionary['site'] = item_dictionary['site']

        return tasks_dictionary
