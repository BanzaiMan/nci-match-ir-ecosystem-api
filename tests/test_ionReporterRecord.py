from unittest import TestCase
import boto3
# from resources.ion_reporter_record import IonReporterRecord
from mock import patch

TABLE_NAME = 'ion_reporters'
TABLE_RT = 5
TABLE_WT = 5
TABLE_HK_NAME = u'hash_key'
TABLE_HK_TYPE = u'S'
TABLE_RK_NAME = u'range_key'
TABLE_RK_TYPE = u'S'

HK_VALUE = u'ion_reporter_id'
RK_VALUE = u'Decode this data if you are a coder'

ITEM = {
    TABLE_HK_NAME: {TABLE_HK_TYPE: HK_VALUE},
    TABLE_RK_NAME: {TABLE_RK_TYPE: RK_VALUE},
    u'ion_reporter_id': {u'S': u'IR_WO3IA'},
}

import sys
sys.path.append('..')


class TestIonReporterRecord(TestCase):

    def setUp(self):

        from ddbmock import connect_boto_patch
        from ddbmock.database.db import dynamodb
        from ddbmock.database.table import Table
        from ddbmock.database.key import PrimaryKey

        # Do a full database wipe
        dynamodb.hard_reset()

        # Instanciate the keys
        hash_key = PrimaryKey(TABLE_HK_NAME, TABLE_HK_TYPE)
        range_key = PrimaryKey(TABLE_RK_NAME, TABLE_RK_TYPE)

        # Create a test table and register it in ``self`` so that you can use it directly
        self.t1 = Table(TABLE_NAME, TABLE_RT, TABLE_WT, hash_key, range_key)

        # Very important: register the table in the DB
        dynamodb.data[TABLE_NAME]  = self.t1

        # Unconditionally add some data, for example.
        self.t1.put(ITEM, {"ion_reporter_id": {"S": "IR_WO3IA"}, "ip_address": {"S": "129.43.39.182"}, "internal_ip_address": {"S": "129.43.39.182"}, "host_name": {"S": "NCI-MATCH-IR"}, "site": {"S": "mocha"}, "status": {"S": "Contacted 4 minutes ago"}, "last_contact": {"S": "August 29, 2016 2:01 PM GMT"}, "data_files": {"S": "DB Report"}})

        # Create the database connection ie: patch boto
        self.db = connect_boto_patch()

    def tearDown(self):
        from ddbmock.database.db import dynamodb
        from ddbmock import clean_boto_patch

        # Do a full database wipe
        dynamodb.hard_reset()

        # Remove the patch from Boto code (if any)
        clean_boto_patch()

    def test_get_hr(self):
        from ddbmock.database.db import dynamodb

        # Example test
        expected = {
            u'ConsumedCapacityUnits': 0.5,
            u'Item': ITEM,
        }

        key = {
            u"HashKeyElement":  {TABLE_HK_TYPE: HK_VALUE},
            u"RangeKeyElement": {TABLE_RK_TYPE: RK_VALUE},
        }

        # Example chech
        self.assertEquals(expected, self.db.layer1.get_item(TABLE_NAME, key))