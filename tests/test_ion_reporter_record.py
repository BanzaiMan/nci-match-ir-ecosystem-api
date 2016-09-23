import unittest
import app
import json
from ddt import ddt, data, unpack
from mock import patch


@ddt
class TestIonReporterRecord(unittest.TestCase):
    def setUp(self):
        # Starting flask server
        self.app = app.app.test_client()

    # TODO:Waleed why is the return code 200 when there is no data in the database_data variable on the first and last run of this method?
    # @data(
    #         ([{}, {}], 'IR_AIO78', {'projection': ['site', 'ir_status']}, 200),
    #         ({}, 'IR_WO4IA', None, 404),
    #         ({}, '', None, 404),
    #         ([{}, {}], 'IR_AIO78', {'projection': None}, 200),
    # )
    # @unpack
    # @patch('resources.ion_reporter_record.IonReporterAccessor')
    # @patch('resources.sequence_data.reqparse.RequestParser.parse_args')
    # def test_get(self, database_data, ion_reporter_id, args, expected_results, mock_parse_args_function, mock_class):
    #     instance = mock_class.return_value
    #     instance.scan.return_value = database_data
    #     mock_parse_args_function.return_value = args
    #     return_value = self.app.get('/api/v1/ion_reporters/' + ion_reporter_id)
    #     assert return_value.status_code == expected_results
    #     if expected_results == 200:
    #         assert len(return_value.data) > 0
    #         print json.loads(return_value.data)
    #         assert (json.loads(return_value.data)) == database_data
    #     else:
    #         assert return_value.data.find("message")

    @patch('resources.ion_reporter_record.IonReporterAccessor')
    def test_get_exception(self, mock_class):
        instance = mock_class.return_value
        instance.get_item.side_effect = Exception('testing throwing exception')
        return_value = self.app.get('/api/v1/ion_reporters/IR_WO3IA')
        assert return_value.status_code == 500
        assert "testing throwing exception" in return_value.data

    @data(
        ('IR_WO3IA', '"message": "Item deleted"')
    )
    @unpack
    @patch('resources.ion_reporter_record.CeleryTaskAccessor')
    def test_delete(self, ion_reporter_id, expected_results, mock_class):
        instance = mock_class.return_value
        instance.delete_ir_item.return_value = True
        return_value = self.app.delete('/api/v1/ion_reporters/' + ion_reporter_id)
        print "return data=" + str(return_value.data)
        assert expected_results in return_value.data

    @patch('resources.ion_reporter_record.CeleryTaskAccessor')
    def test_delete_exception(self, mock_class):
        instance = mock_class.return_value
        instance.delete_ir_item.side_effect = Exception('testing throwing exception')
        return_value = self.app.delete('/api/v1/ion_reporters/IR_WO3IA')
        assert return_value.status_code == 500
        assert "testing throwing exception" in return_value.data

    @data(
        ('IR_WO3IA',
         {"status": "Contacted 5 minutes ago"}, 'Ion reporter with ion reporter id'),
        ('IR_WO3IA', None, 'Update item failed')
    )
    @unpack
    @patch('resources.ion_reporter_record.CeleryTaskAccessor')
    def test_put(self, ion_reporter_id, item, expected_results, mock_class):
        instance = mock_class.return_value
        instance.update_ir_item.return_value = True
        return_value = self.app.put('/api/v1/ion_reporters/' + ion_reporter_id,
                                    data=json.dumps(item),
                                    content_type='application/json')
        print return_value.data
        assert expected_results in return_value.data

    @patch('resources.ion_reporter_record.CeleryTaskAccessor')
    def test_put_exception(self, mock_class):
        instance = mock_class.return_value
        instance.update_ir_item.side_effect = Exception('Ion reporter creation failed')
        return_value = self.app.put('/api/v1/ion_reporters/IR_WO3IA',
                                    data='{"status":"Lost contact! Last heartbeat was sent 11355 minutes ago"}',
                                    headers={'Content-Type': 'application/json'})
        print return_value.status_code
        assert return_value.status_code == 404
        assert "No ion reporters with id" in return_value.data


# if __name__ == '__main__':
#     unittest.main()
