import urllib
import json

SC_URL = "http://localhost:5000"
PT_URL = "http://localhost:10240"


class PatientEcosystemIntegrator(object):

    # @staticmethod
    # def retrieve_url(url):
    #     response = urllib.urlopen(SC_URL + '/api/v1/sample_controls/SC_SA1C')
    #     json_data = json.loads(response.read())
    #     return json_data

    @staticmethod
    def verify_molecular_id(molecular_id):

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
                return json_data_pt


if __name__ == '__main__':
    result1 = PatientEcosystemIntegrator().verify_molecular_id('SC_SA1CB')
    result2 = PatientEcosystemIntegrator().verify_molecular_id('SC_SA1C')
    result3 = PatientEcosystemIntegrator().verify_molecular_id('PT_SR10_BdVRRejected_BD_MOI1')
    result4 = PatientEcosystemIntegrator().verify_molecular_id('44')
    print result1
    print result2
    print result3
    print result4




# http://localhost:10240/api/v1/shipments/PT_SR10_BdVRRejected_BD_MOI1