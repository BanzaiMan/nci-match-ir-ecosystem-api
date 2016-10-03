import urllib
import json
import logging
from string import Template
from resource_helpers.abort_logger import AbortLogger

URL = "http://localhost:10240"

MESSAGE_404 = Template("No molecular id with id: $molecular_id found")
MESSAGE_500 = Template("Server Error could not connect to patient ecosystem APIcontact help: $error")

# http://localhost:10240/api/v1/shipments/PT_SR10_BdVRRejected_BD_MOI1 temporary record

class PatientEcosystemConnector(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def verify_molecular_id(self, molecular_id):

        self.logger.info("Checking if molecular id: " + str(molecular_id) + " is in patient table")
        url = (URL + "/api/v1/shipments/")

        try:
            json_data = PatientEcosystemConnector.open_url(url, molecular_id)
        except Exception as e:
            AbortLogger.log_and_abort(500, self.logger.error, MESSAGE_500.substitute(error=e.message))

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
