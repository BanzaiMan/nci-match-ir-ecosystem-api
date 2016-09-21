from unittest import TestCase

TABLE_NAME = 'ion_reporters'
TABLE_RT = 5
TABLE_WT = 5
TABLE_HK_NAME = u'ion_reporter_id'
TABLE_HK_TYPE = u'S'

HK_VALUE = u'IR_5467A'

ITEM = {
    TABLE_HK_NAME: {TABLE_HK_TYPE: HK_VALUE},
    u'test': {u'S': u'something goes here'}
}


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
        self.t1.put(ITEM, {})

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
        from ddbmock import connect_boto_patch
        from ddbmock.database.db import dynamodb

        # Example test
        expected = {
            u'ConsumedCapacityUnits': 0.5,
            u'Item': ITEM,
        }

        key = {
            u"HashKeyElement":  {TABLE_HK_TYPE: HK_VALUE}
        }

        # Example check
        self.assertEquals(expected, self.db.layer1.get_item(TABLE_NAME, key))

        # Example check
        #self.assertEquals(expected, self.db.layer1.scan(TABLE_NAME, 'test', 'EQ', 'something goes here'))

