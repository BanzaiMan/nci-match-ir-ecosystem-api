from unittest import TestCase
from mock import patch
from ddt import ddt, data, unpack
from accessors.dynamodb_accessor import DynamoDBAccessor
from accessors.ion_reporter_accessor import IonReporterAccessor

TABLE_NAME = 'ion_reporters'
TABLE_RT = 5
TABLE_WT = 5
TABLE_HK_NAME = u'ion_reporter_id'
TABLE_HK_TYPE = u'S'

HK_VALUE = u'IR_5467A'

HK_VALUE2 = u'IR_AIO78'

ITEM = {
    TABLE_HK_NAME: {TABLE_HK_TYPE: HK_VALUE},
    u'test': {u'S': u'something goes here'}
}

ITEM2 = {
    # TABLE_HK_NAME: {TABLE_HK_TYPE: HK_VALUE2},
    # u'Item': {u'ir_status': u'Contacted 4 minutes ago'}
     # 'ResponseMetadata': {'RetryAttempts': 0, 'HTTPStatusCode': 200,
     #                      'RequestId': '76a79e52-70f6-453b-806f-3931abac715a',
     #                      'HTTPHeaders': {'x-amzn-requestid': '76a79e52-70f6-453b-806f-3931abac715a',
     #                                      'content-length': '75', 'content-type': 'application/x-amz-json-1.0',
     #                                      'x-amz-crc32': '2724516794', 'server': 'Jetty(8.1.12.v20130726)'}}
    TABLE_HK_NAME: {TABLE_HK_TYPE: HK_VALUE2},
    "ion_reporter_id": {"S": "IR_AIO78"},
    "ip_address": {"S": "132.183.13.75"},
    "internal_ip_address": {"S": "172.20.174.24"},
    "host_name": {"S": "MDACC-MATCH-IR"},
    "site": {"S": "mdacc"},
    "ir_status": {"S": "Contacted 4 minutes ago"},
    "last_contact": {"S": "August 29, 2016 2:01 PM GMT"},
    "data_files": {"S": "Log File"}
}


TABLE_HK_NAME2 = u'ir_status'


@ddt
class TestIonReporterRecord(TestCase):
        def setUp(self):
            from ddbmock import connect_boto_patch
            from ddbmock.database.db import dynamodb
            from ddbmock.database.table import Table
            from ddbmock.database.key import PrimaryKey

            # Do a full database wipe
            dynamodb.hard_reset()

            # Instantiate the keys
            hash_key = PrimaryKey(TABLE_HK_NAME, TABLE_HK_TYPE)

            # Create a test table and register it in ``self`` so that you can use it directly
            self.t1 = Table(TABLE_NAME, TABLE_RT, TABLE_WT, hash_key, None)

            # Very important: register the table in the DB
            dynamodb.data[TABLE_NAME] = self.t1

            # Unconditionally add some data, for example.
            self.t1.put(ITEM2, {})

            # Create the database connection ie: patch boto
            self.db = connect_boto_patch()

        def tearDown(self):
            from ddbmock.database.db import dynamodb
            from ddbmock import clean_boto_patch

            # Do a full database wipe
            dynamodb.hard_reset()

            # Remove the patch from Boto code (if any)
            clean_boto_patch()

        # @data(
        #     ({'ion_reporter_id': u'IR_AIO78'}, '')
        # )

        # @patch('accessors.dynamodb_accessor.DynamoDBAccessor')
        @patch('accessors.ion_reporter_accessor.IonReporterAccessor')
        def test_get_item(self, mock_IR_accessor):
            from ddbmock import connect_boto_patch
            from ddbmock.database.db import dynamodb

            # Example test
            expected = {
                u'ConsumedCapacityUnits': 0.5,
                u'Item': ITEM2,
            }


            key = {
                u"HashKeyElement": {TABLE_HK_TYPE: HK_VALUE2}
            }

            instance = mock_IR_accessor.return_value
            instance.get_item.return_value = expected

            return_value = self.db.layer1.get_item(TABLE_NAME, key)

            self.assertEquals(return_value, self.db.layer1.get_item(TABLE_NAME, key))