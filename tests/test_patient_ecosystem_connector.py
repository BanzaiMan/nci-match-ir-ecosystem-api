import unittest
from unittest import TestCase
from ddt import ddt, data, unpack
from common.patient_ecosystem_connector import PatientEcosystemConnector
from mock import patch
import mock
import __builtin__
import app


@ddt
class TestPatientEcosystemConnector(TestCase):

    def setUp(self):

        self.patient_ecosystem_connector = PatientEcosystemConnector()

    @data(
        ('SC_SA1CB', 404, {}),
        ('', 404, {}),
        ('', 500, {}),
        ('PT_VU16_BdVRUploaded_BD_MOI1', 200, {"uuid":"98fb0d64-27af-4237-8fbe-22abc0ad2bb8",
                                          "shipped_date":"2016-05-01T19:42:13+00:00",
                                          "patient_id":"PT_VU16_BdVRUploaded",
                                          "molecular_id":"PT_VU16_BdVRUploaded_BD_MOI1",
                                          "study_id":"APEC1621","type":"BLOOD_DNA","carrier":"Federal Express",
                                          "tracking_id":"7956 4568 1235","destination":"MDA","dna_volume_ul":"10.0",
                                          "dna_concentration_ng_per_ul":"25.0","cdna_volume_ul":"10.0"}),
    )
    @unpack
    @patch('common.patient_ecosystem_connector.requests.get')
    def test_verify_molecular_id(self, molecular_id, expected_statuscode, expected_result, mock_get):
        """
                Test getting a 200 OK response and 404 from the open_url method of PatientEcosystemConnector.
                """
        # Construct our mock response object, giving it relevant expected
        # behaviours

        mock_response = mock.Mock()
        mock_response.json.return_value = expected_result
        mock_response.status_code = expected_statuscode

        # Assign our mock response as the result of our patched function
        mock_get.return_value = mock_response

        url = (__builtin__.environment_config[__builtin__.environment]['patient_endpoint']
               + __builtin__.environment_config[__builtin__.environment]['shipments_path'] + molecular_id)

        (response_status, response_data) = self.patient_ecosystem_connector.verify_molecular_id(molecular_id=molecular_id)

        # Check that our function made the expected internal calls
        # mock_get.assert_called_once_with(url)
        # print mock_response.json.call_count
        # self.assertEqual(1, mock_response.json.call_count)

        print response_status
        print response_data
        self.assertEqual(response_status, expected_statuscode)
        self.assertEqual(response_data, expected_result)


    @data('PT_VU16_BdVRUploaded_BD_MOI1')
    @patch('common.patient_ecosystem_connector.requests')
    def test_get_exception(self, molecular_id, mock_class):
        # Testing exception

        #instance = mock_class.return_value
        mock_class.get.side_effect = Exception('testing throwing exception')
        try:
            (response_status, response_data) = PatientEcosystemConnector().verify_molecular_id(molecular_id)
        except Exception as e:
            assert "testing throwing exception" in e.message
        else:
            assert False



    #
    # if __name__ == "__main__":
    #     unittest.main()
