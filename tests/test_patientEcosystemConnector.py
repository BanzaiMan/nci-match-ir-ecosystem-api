# from unittest import TestCase
# from ddt import ddt, data, unpack
# from common.patient_ecosystem_connector import PatientEcosystemConnector
#
# @ddt
# class TestPatientEcosystemConnector(TestCase):
#     @data(
#         ('SC_SA1CB', {'control_type': u'no_template', 'molecular_id': u'SC_SA1CB'}),
#         ('SC_SA1C', '404: Not Found'),
#         ('PT_SR10_BdVRRejected_BD_MOI1', [{u'dna_concentration_ng_per_ul': u'25.0',
#                                            u'uuid': u'69cf6ae8-d95b-463a-be4e-1ba2b7ebdf04',
#                                            u'dna_volume_ul': u'10.0', u'destination': u'MDA',
#                                            u'patient_id': u'PT_SR10_BdVRRejected',
#                                            u'shipped_date': u'2016-05-01T19:42:13+00:00',
#                                            u'study_id': u'APEC1621', u'carrier': u'Federal Express',
#                                            u'tracking_id': u'7956 4568 1235', u'cdna_volume_ul': u'10.0',
#                                            u'type': u'BLOOD_DNA', u'molecular_id': u'PT_SR10_BdVRRejected_BD_MOI1'}]),
#         # ('44', '404: Not Found')
#     )
#     @unpack
#     def test_verify_molecular_id(self, molecular_id, expected_result):
#         try:
#             print PatientEcosystemConnector().verify_molecular_id(molecular_id)
#             assert PatientEcosystemConnector().verify_molecular_id(molecular_id) == expected_result
#         except Exception as e:
#             print e
#             assert str(e) == expected_result

