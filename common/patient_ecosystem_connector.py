import requests
import json
from flask_restful import abort
import __builtin__


class PatientEcosystemConnector(object):
    """This class is for connecting with the patient ecosystem in order to verify if the molecular id exists in
    the patient ecosystem database"""

    @staticmethod
    def verify_molecular_id(molecular_id):

        url = (__builtin__.environment_config[__builtin__.environment]['patient_endpoint']
               + __builtin__.environment_config[__builtin__.environment]['shipments_path'])

        try:
            request_data = PatientEcosystemConnector.open_url(url, molecular_id)

            return request_data
        except Exception as e:
            abort(500, message="Failed to connect to patient ecosystem, because : " + e.message)

    @staticmethod
    def open_url(url, molecular_id):

        lookup_url = (url + molecular_id)
        request_data = requests.get(lookup_url).json.return_value

        return request_data