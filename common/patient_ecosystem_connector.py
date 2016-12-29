import requests
import logging
import __builtin__


class PatientEcosystemConnector(object):
    """This class is for connecting with the patient ecosystem in order to verify if the molecular id exists in
    the patient ecosystem database"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def verify_molecular_id(self, molecular_id, auth_token):
        self.logger.debug("Checking if molecular id: " + str(molecular_id) + " is in patient ecosystem")
        self.logger.debug("Retrieving ID token.")

        # id_token = Auth0Authenticate.get_id_token()
        headers = {'authorization': auth_token}

        url = (__builtin__.environment_config[__builtin__.environment]['patient_endpoint']
               + __builtin__.environment_config[__builtin__.environment]['shipments_path'])

        try:
            request = requests.get(url + molecular_id, headers=headers)
        except Exception as e:
            self.logger.error("Unable to connect to patient ecosystem: " + str(e))
            raise
        else:
            if request.status_code == 200:
                return request.status_code, request.json()
            else:
                return request.status_code, {}
