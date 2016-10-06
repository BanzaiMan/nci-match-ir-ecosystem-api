import requests
import __builtin__


class PatientEcosystemConnector(object):

    @staticmethod
    def verify_molecular_id(molecular_id):

        url = (__builtin__.environment_config[__builtin__.environment]['patient_endpoint'] + "/api/v1/shipments/")
        try:
            json_data = PatientEcosystemConnector.open_url(url, molecular_id)
        except Exception as e:
            raise Exception("Failed to connect to patient ecosystem, because : " + e.message)

        if len(json_data) > 0:
            return json_data
        else:
            raise Exception("Failed to connect to patient ecosystem, because : ")

    @staticmethod
    def open_url(url, molecular_id):

        lookup_url = (url + molecular_id)
        json_data = requests.get(lookup_url)

        return json_data.json()