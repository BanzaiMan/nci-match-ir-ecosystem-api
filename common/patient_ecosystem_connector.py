import requests
import __builtin__


class PatientEcosystemConnector(object):
    """This class is for connecting with the patient ecosystem in order to verify if the molecular id exists in
    the patient ecosystem database"""

    def verify_molecular_id(self, molecular_id):

        url = (__builtin__.environment_config[__builtin__.environment]['patient_endpoint']
               + __builtin__.environment_config[__builtin__.environment]['shipments_path'])
        try:
            request_data = requests.get(url + molecular_id).json()
        except Exception as e:
            # need a logger
            raise
        else:
            return request_data
