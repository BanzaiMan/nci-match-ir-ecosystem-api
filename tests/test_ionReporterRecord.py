import unittest
import app
import json
from ddt import ddt, data, unpack
from mock import patch, MagicMock, Mock


@ddt
class TestIonReporterTable(unittest.TestCase):
    def setUp(self):
        # Starting flask server
        self.app = app.app.test_client()


    @data(
            ({"status": "Contacted 5 minutes ago", "last_contact": "August 29, 2016 2:00 PM GMT"}, 'IR_WO3IA', 200),
            ({}, 'IR_WO4IA', 404)
    )
    @unpack
    @patch('resources.ion_reporter_record.IonReporterAccessor')
    def test_get(self, database_data, ion_reporter_id, expected_results, mock_class):
        instance = mock_class.return_value
        instance.scan.return_value = database_data
        return_value = self.app.get('/api/v1/ion_reporters/' + ion_reporter_id)
        assert return_value.status_code == expected_results
        if expected_results == 200:
            assert len(return_value.data) > 0
            assert (json.loads(return_value.data))['status'] == "Contacted 5 minutes ago"
        else:
            assert return_value.data.find("message")

    @patch('resources.ion_reporter_record.IonReporterAccessor')
    def test_get_exception(self, mock_class):
        instance = mock_class.return_value
        instance.scan.side_effect = Exception('testing throwing exception')
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
         {"status": "Contacted 6 minutes ago"}, 'Ion reporter with ion reporter id'),
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
        assert expected_results in return_value.data

    @patch('resources.ion_reporter_record.CeleryTaskAccessor')
    def test_put_exception(self, mock_class):
        instance = mock_class.return_value
        instance.update_ir_item.side_effect = Exception('Ion reporter creation failed')
        return_value = self.app.put('/api/v1/ion_reporters/IR_WO3IA',
                                    data='{"status":"Lost contact! Last heartbeat was sent 11355 minutes ago"}',
                                    headers={'Content-Type': 'application/json'})
        assert return_value.status_code == 500
        assert "Ion reporter creation failed" in return_value.data


if __name__ == '__main__':
    unittest.main()
