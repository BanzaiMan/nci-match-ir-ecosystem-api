import unittest
import os.path
import sys
from mock import patch, MagicMock
from ddt import ddt, data, unpack

sys.path.append("..")
from dynamodb import aws
#from s3_transfer import aws


@ddt
class TestDynamodbService(unittest.TestCase):

    def setUp(self):
        pass
# TODO: write unittests
if __name__ == '__main__':
    unittest.main()
