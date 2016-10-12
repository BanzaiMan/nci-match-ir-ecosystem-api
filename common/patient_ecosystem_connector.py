import requests
import logging
import __builtin__


class PatientEcosystemConnector(object):
    """This class is for connecting with the patient ecosystem in order to verify if the molecular id exists in
    the patient ecosystem database"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def verify_molecular_id(self, molecular_id):
        # TODO: Waleed.. this is probably best if it was set to debug as we don't necessarily need to see this all the time.
        self.logger.info("Checking if molecular id: " + str(molecular_id) + " is in patient ecosystem")

        url = (__builtin__.environment_config[__builtin__.environment]['patient_endpoint']
               + __builtin__.environment_config[__builtin__.environment]['shipments_path'])
        try:
            request_data = requests.get(url + molecular_id).json()
        except Exception as e:
            # TODO: Waleed.. this is an error  not "info" need to use error
            self.logger.info("Unable to connect to patient ecosystem: " + str(e))
            raise
        else:
            return request_data
