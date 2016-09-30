import urllib
import json
import logging
from string import Template
from flask_restful import request, Resource
from resource_helpers.abort_logger import AbortLogger


SC_URL = "http://localhost:5000"
PT_URL = "http://localhost:10240"

MESSAGE_404 = Template("No molecular id with id: $molecular_id found")

# http://localhost:10240/api/v1/shipments/PT_SR10_BdVRRejected_BD_MOI1 temporary record

class PatientEcosystemConnector(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def verify_molecular_id(self, molecular_id):

        self.logger.info("Checking if molecular id: " + str(molecular_id) + " is in sample control table or patient ecosystem")

        lookup_sc_url = urllib.urlopen(SC_URL + '/api/v1/sample_controls/' + molecular_id)
        json_data_sc = json.loads(lookup_sc_url.read())

        if len(json_data_sc) > 1:
            return {'molecular_id': json_data_sc['molecular_id'], 'control_type' : json_data_sc['control_type']}
        else:
            response = urllib.urlopen(PT_URL + '/api/v1/shipments/' + molecular_id)
            json_data_pt = json.loads(response.read())
            if len(json_data_pt) > 0:
                return json_data_pt
            else:
                AbortLogger.log_and_abort(404, self.logger.debug,
                                          MESSAGE_404.substitute(molecular_id=molecular_id))

    def verify_sc_molecular_id(self, molecular_id):

        self.logger.info("Checking if molecular id: " + str(molecular_id) + " is in sample control table")
        url = "http://localhost:5000/api/v1/sample_controls/"
        json_data = PatientEcosystemConnector.open_url(url, molecular_id)

        if len(json_data) > 1:
            return {'molecular_id': json_data['molecular_id'], 'control_type' : json_data['control_type']}
        else:
            AbortLogger.log_and_abort(404, self.logger.debug,
                                        MESSAGE_404.substitute(molecular_id=molecular_id))

    def verify_pt_molecular_id(self, molecular_id):

        self.logger.info("Checking if molecular id: " + str(molecular_id) + " is in sample control table")
        url = "http://localhost:10240/api/v1/shipments/"
        json_data = PatientEcosystemConnector.open_url(url, molecular_id)

        if len(json_data) > 0:
            return json_data
        else:
            AbortLogger.log_and_abort(404, self.logger.debug,
                                      MESSAGE_404.substitute(molecular_id=molecular_id))

    @staticmethod
    def open_url(url, molecular_id):

        lookup_url = urllib.urlopen(url + molecular_id)
        json_data = json.loads(lookup_url.read())
        return json_data

