from unittest import TestCase


# class TestDynamoDBAccessor(TestCase):
#     def test_scan(self):
#         self.fail()
#
#     def test_put_item(self):
#         self.fail()
#
#     def test_update_item(self):
#         self.fail()
#
#     def test_get_item(self):
#         self.fail()
#
#     def test_delete_item(self):
#         self.fail()
#
#     def test_batch_writer(self):
#         self.fail()
#
#     def test_delete_table(self):
#         self.fail()
#
#     def test_batch_delete(self):
#         self.fail()
#
#     def test_create_table(self):
#         self.fail()
#
#     def test_handle_table_creation(self):
#         self.fail()

# from unittest import TestCase
#
# TABLE_NAME = 'ion_reporters'
# TABLE_RT = 45
# TABLE_WT = 123
# TABLE_HK_NAME = u'hash_key'
# TABLE_HK_TYPE = u'S'
# TABLE_RK_NAME = u'range_key'
# TABLE_RK_TYPE = u'S'
#
# HK_VALUE = u'ion_reporter_id'
# RK_VALUE = u'Decode this data if you are a coder'
#
# ITEM = {
#     TABLE_HK_NAME: {TABLE_HK_TYPE: HK_VALUE},
#     TABLE_RK_NAME: {TABLE_RK_TYPE: RK_VALUE},
#     u'ion_reporter_id': {u'S': u'IR_WO3IA'},
# }
#
# import sys
# sys.path.append('..')
#
#
# class TestIonReporterRecord(TestCase):
#     def setUp(self):
#         from ddbmock import connect_boto_patch
#         from ddbmock.database.db import dynamodb
#         from ddbmock.database.table import Table
#         from ddbmock.database.key import PrimaryKey
#
#         # Do a full database wipe
#         dynamodb.hard_reset()
#
#         # Instanciate the keys
#         hash_key = PrimaryKey(TABLE_HK_NAME, TABLE_HK_TYPE)
#         range_key = PrimaryKey(TABLE_RK_NAME, TABLE_RK_TYPE)
#
#         # Create a test table and register it in ``self`` so that you can use it directly
#         self.t1 = Table(TABLE_NAME, TABLE_RT, TABLE_WT, hash_key, range_key)
#
#         # Very important: register the table in the DB
#         dynamodb.data[TABLE_NAME]  = self.t1
#
#         # Unconditionally add some data, for example.
#         self.t1.put(ITEM, {})
#
#         #   self.t1.put(ITEM, {"date_molecular_id_created": {"S": "2016-08-22 19:56:19.766"},
#       # "control_type": {"S": "no_template"},
#       # "site_ip_address": {"S": "129.43.127.133"},
#       # "molecular_id": {"S": "SC_5AMCC"},
#       # "site": {"S": "mocha"}})
#
#         # Create the database connection ie: patch boto
#         self.db = connect_boto_patch()
#
#     def tearDown(self):
#         from ddbmock.database.db import dynamodb
#         from ddbmock import clean_boto_patch
#
#         # Do a full database wipe
#         dynamodb.hard_reset()
#
#         # Remove the patch from Boto code (if any)
#         clean_boto_patch()
#
#     def test_get_hr(self):
#         from ddbmock import connect_boto_patch
#         from ddbmock.database.db import dynamodb
#
#         # Example test
#         expected = {
#             u'ConsumedCapacityUnits': 0.5,
#             u'Item': ITEM,
#         }
#
#         key = {
#             u"HashKeyElement":  {TABLE_HK_TYPE: HK_VALUE},
#             u"RangeKeyElement": {TABLE_RK_TYPE: RK_VALUE},
#         }
#
#         # Example chech
#         self.assertEquals(expected, self.db.layer1.get_item(TABLE_NAME, key))
#
#     def test_scan(self):
#         from ddbmock import connect_boto_patch
#         from ddbmock.database.db import dynamodb
#
#         # Example test
#         expected = {u'Count': 1, u'Items': [{u'status': u'Contacted 4 minutes ago',
#                                              u'last_contact': u'August 29, 2016 2:01 PM GMT',
#                                              u'internal_ip_address': u'172.20.174.24',
#                                              u'site': u'mdacc', u'host_name': u'MDACC-MATCH-IR',
#                                              u'data_files': u'Log File', u'ip_address': u'132.183.13.75',
#                                              u'ion_reporter_id': u'IR_AIO78'}], u'ScannedCount': 5,
#                     'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '5513cfd4-7a1c-443a-9a51-6b893f4a941f',
#                                          'HTTPHeaders': {'x-amzn-requestid': '5513cfd4-7a1c-443a-9a51-6b893f4a941f',
#                                                          'content-length': '332', 'content-type': 'application/x-amz-json-1.0',
#                                                          'x-amz-crc32': '640366951', 'server': 'Jetty(8.1.12.v20130726)'}}}
#
#         key = {
#             u"HashKeyElement":  {TABLE_HK_TYPE: HK_VALUE},
#             #u"RangeKeyElement": {TABLE_RK_TYPE: RK_VALUE},
#         }
#
#         # Example chech
#         self.assertEquals(expected, self.db.layer1.scan(TABLE_NAME, key))