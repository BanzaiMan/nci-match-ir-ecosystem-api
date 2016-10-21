import requests
import logging
import __builtin__


class PatientEcosystemConnector(object):
    """This class is for connecting with the patient ecosystem in order to verify if the molecular id exists in
    the patient ecosystem database"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def verify_molecular_id(self, molecular_id):
        self.logger.debug("Checking if molecular id: " + str(molecular_id) + " is in patient ecosystem")
        url = (__builtin__.environment_config[__builtin__.environment]['patient_endpoint']
               + __builtin__.environment_config[__builtin__.environment]['shipments_path'])
        try:
            request = requests.get(url + molecular_id)
        except Exception as e:
            self.logger.error("Unable to connect to patient ecosystem: " + str(e))
            raise
        else:
            return request
