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

    @data(
            ({'ir_status': 'Contacted 4 minutes ago', 'site': 'mdacc'}, 'IR_AIO78', {'projection': ['site', 'ir_status']}, 200),
            ({}, 'IR_WO4IA', None, 404),
            ({}, '', None, 404),
            (None, 'IR_AIO78', {'projection': None}, 500),
    )
    @unpack
    @patch('resources.ion_reporter_record.IonReporterAccessor')
    @patch('resources.sequence_data.reqparse.RequestParser.parse_args')
    def test_get(self, database_data, ion_reporter_id, args, expected_results, mock_parse_args_function, mock_class):
        instance = mock_class.return_value
        instance.get_item.return_value = database_data
        mock_parse_args_function.return_value = args

        if args is not None and args['projection'] is not None:
            projection_list = args['projection']
            return_value = self.app.get('/api/v1/ion_reporters/' + ion_reporter_id + '?projection=' + projection_list[0] + '?projection=' + projection_list[1])
        else:
            return_value = self.app.get('/api/v1/ion_reporters/' + ion_reporter_id)
        print return_value.status_code

        assert return_value.status_code == expected_results
        if expected_results == 200:
            assert len(return_value.data) > 0
            print json.loads(return_value.data)
            assert (json.loads(return_value.data)) == database_data
        else:
            assert return_value.data.find("message")

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
    @patch('resources.record.Record.record_exist')
    @patch('resources.ion_reporter_record.CeleryTaskAccessor')
    def test_delete(self, ion_reporter_id, expected_results, mock_class, mock_method):
        # TODO: Change to pass in True or False from data runner to test different conditions
        mock_method.return_value = True
        instance = mock_class.return_value
        instance.delete_ir_item.return_value = True
        return_value = self.app.delete('/api/v1/ion_reporters/' + ion_reporter_id)
        print "return data=" + str(return_value.data)
        assert expected_results in return_value.data

    @patch('resources.record.Record.record_exist')
    @patch('resources.ion_reporter_record.CeleryTaskAccessor')
    def test_delete_exception(self, mock_class, mock_method):
        # TODO: Change to pass in True or False from data runner to test different conditions
        mock_method.return_value = True
        instance = mock_class.return_value
        instance.delete_ion_reporter_record.side_effect = Exception('Celery Task Accessor blew up!')
        return_value = self.app.delete('/api/v1/ion_reporters/IR_WO3IA')
        assert return_value.status_code == 500
        assert "Celery Task Accessor blew up!" in return_value.data

    # TODO: This needs more tests to make sure all exceptions and paths are executed in the test
    @data(
        ('IR_WO3IA',
         {"status": "Contacted 5 minutes ago"}, 'updated', True, 200),
        ('IR_WO3IA', None, 'Update item failed', True, 400),
        ('IR_WO3IA', {"status": "Contacted 5 minutes ago"}, ' with id: ', False, 404)
    )
    @unpack
    @patch('resources.record.Record.record_exist')
    @patch('resources.ion_reporter_record.CeleryTaskAccessor')
    def test_put(self, ion_reporter_id, item, expected_results, item_in_database, return_status, mock_class, mock_method):
        mock_method.return_value = item_in_database
        instance = mock_class.return_value
        instance.update_ion_reporter_record.return_value = True
        return_value = self.app.put('/api/v1/ion_reporters/' + ion_reporter_id,
                                    data=json.dumps(item),
                                    content_type='application/json')

        assert return_value.status_code == return_status
        assert expected_results in return_value.data

    @patch('resources.record.Record.record_exist')
    @patch('resources.ion_reporter_record.CeleryTaskAccessor')
    def test_put_exception(self, mock_class, mock_method):
        mock_method.return_value = True
        instance = mock_class.return_value
        instance.update_ion_reporter_record.side_effect = Exception('Celery Failed')
        return_value = self.app.put('/api/v1/ion_reporters/IR_WO3IA',
                                    data='{"status":"Lost contact! Last heartbeat was sent 11355 minutes ago"}',
                                    headers={'Content-Type': 'application/json'})

        assert return_value.status_code == 500
        assert "Celery Failed" in return_value.data


# if __name__ == '__main__':
#     unittest.main()
