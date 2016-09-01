# from unittest import TestCase
# from common.datetime_helper import DateTimeHelper
# from ddt import ddt, data, unpack
# from mock import patch
# import datetime
#
# class TestDateTimeHelper(TestCase):
#
#     @patch('datetime.datetime')
#     def test_get_utc_millisecond_timestamp(self, dt_mock, micro_mock):
#         dt_mock.utcnow.return_value.strftime.return_value = '2016-08-04 12:22:44.123456'
#         result = DateTimeHelper.get_utc_millisecond_timestamp()
#         testdt = datetime.datetime(2016, 8, 4, 12, 22, 44, 123456)
#         dt_mock.utcnow.return_value = testdt
#         result = DateTimeHelper.get_utc_millisecond_timestamp()
#         assert DateTimeHelper.get_utc_millisecond_timestamp(dt_mock) == result