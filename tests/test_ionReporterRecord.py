# from unittest import TestCase
# import boto
# from resources.ion_reporter_record import IonReporterRecord
#
# TABLE_NAME = 'ion_reporters'
# TABLE_RT = 45
# TABLE_WT = 123
# TABLE_HK_NAME = u'hash_key'
# TABLE_HK_TYPE = u'S'
#
# HK_VALUE = u'ion_reporter_id'
#
# ITEM = {
#     TABLE_HK_NAME: {TABLE_HK_TYPE: HK_VALUE},
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
#
#         # Create a test table and register it in ``self`` so that you can use it directly
#         self.t1 = Table(TABLE_NAME, TABLE_RT, TABLE_WT, hash_key)
#
#         # Very important: register the table in the DB
#         dynamodb.data[TABLE_NAME]  = self.t1
#
#         # Unconditionally add some data, for example.
#         self.t1.put(ITEM, {"date_molecular_id_created": {"S": "2016-08-22 19:56:19.766"},
#       "control_type": {"S": "no_template"},
#       "site_ip_address": {"S": "129.43.127.133"},
#       "molecular_id": {"S": "SC_5AMCC"},
#       "site": {"S": "mocha"}})
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
#         }
#
#         # Example chech
#         self.assertEquals(expected, self.db.layer1.get_item(TABLE_NAME, key))