import requests
from flask_restful import abort
import __builtin__


class PatientEcosystemConnector(object):
    """This class is for connecting with the patient ecosystem in order to verify if the molecular id exists in
    the patient ecosystem database"""

    @staticmethod
    def verify_molecular_id(molecular_id):
        pt_eco_route = '/api/v1/shipments/'
        url = (__builtin__.environment_config[__builtin__.environment]['patient_endpoint'] + pt_eco_route)

        try:
            request_data = PatientEcosystemConnector.open_url(url, molecular_id)
            return request_data.json()
        except Exception as e:
            abort(500, message="Failed to connect to patient ecosystem, because : " + e.message)

    @staticmethod
    def open_url(url, molecular_id):

        lookup_url = (url + molecular_id)
        request_data = requests.get(lookup_url)

        return request_data