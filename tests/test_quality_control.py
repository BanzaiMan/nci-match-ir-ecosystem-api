import unittest
from ddt import ddt, data, unpack
from mock import patch
import app
import json
import mock


@ddt
class TestQualityControl(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()

    @data(
        ({
             "control_type": "no_template",
             "date_molecular_id_created": "2016-08-28 16:56:29.333",
             "site_ip_address": "129.43.127.133",
             "molecular_id": "SC_SA1CB",
             "ion_reporter_id": "IR_WAO85",
             "site": "mocha",
             "tsv_name": "IR_WAO85/SC_SA1CB/SC_SA1CB_SC_SA1CB_a888_v1/SC_SA1CB_SC_SA1CB_analysis888_v1.tsv"
         },
         "SC_SA1CB",
        "../scripts/database/SC_SA1CB_SC_SA1CB_analysis888_v1.json", 200,
        "{\"ion_reporter_id\":\"IR_WAO85\",\"molecular_id\":\"SC_SA1CB\",\"analysis_id\":\"SC_SA1CB_SC_SA1CB_a888_v1\",\"filename\":\"SC_SA1CB_SC_SA1CB_analysis888_v1\",\"total_variants\":4684}"
        )
    )
    @unpack
    @mock.patch("codecs.open", create=True)
    @patch('resources.quality_control.S3Accessor')
    @patch('resources.quality_control.SampleControlAccessor')
    def test_get(self, item, molecular_id, downloaded_file_path,
                 expected_results, json_data, mock_SC_class, mock_S3_class, mock_open):
        instance = mock_SC_class.return_value
        instance.get_item.return_value = item
        instance_s3 = mock_S3_class.return_value
        instance_s3.download.return_value = downloaded_file_path
        mock_open.side_effect = [
            mock.mock_open(read_data=json_data).return_value
        ]


        return_value = self.app.get('/api/v1/quality_control/' + molecular_id)
        print "==============" + str(return_value.status_code)
        assert return_value.status_code == expected_results
        print json.loads(return_value.data)['molecular_id']
        assert json.loads(return_value.data)['molecular_id'] == molecular_id

    @data(
        ({},
         "SC_SA1CB",
         "was not found", 404
        )
    )
    @unpack
    @patch('resources.quality_control.SampleControlAccessor')
    def test_get_exception_item_not_found(self, item, molecular_id, exception_message,
                                          expected_results, mock_SC_class):
        instance = mock_SC_class.return_value
        instance.get_item.return_value = item
        return_value = self.app.get('/api/v1/quality_control/' + molecular_id)
        print "==============" + str(return_value.status_code)
        assert return_value.status_code == expected_results
        print return_value.data
        assert exception_message in return_value.data

    @data(
        ({
             "control_type": "no_template",
             "date_molecular_id_created": "2016-08-28 16:56:29.333",
             "site_ip_address": "129.43.127.133",
             "molecular_id": "SC_SA1CB",
             "ion_reporter_id": "IR_WAO85",
             "site": "mocha"
         },
         "SC_SA1CB",
        "../scripts/database/SC_SA1CB_SC_SA1CB_analysis888_v1.json",
         "tsv file s3 path does not exist", 404
        )
    )
    @unpack
    @patch('resources.quality_control.S3Accessor')
    @patch('resources.quality_control.SampleControlAccessor')
    def test_get_exception_tsv_not_found(self, item, molecular_id, downloaded_file_path, exception_message,
                                          expected_results, mock_SC_class, mock_S3_class):
        instance = mock_SC_class.return_value
        instance.get_item.return_value = item
        instance_s3 = mock_S3_class.return_value
        instance_s3.download.return_value = downloaded_file_path
        return_value = self.app.get('/api/v1/quality_control/' + molecular_id)
        print "==============" + str(return_value.status_code)
        assert return_value.status_code == expected_results
        print return_value.data
        assert exception_message in return_value.data

# if __name__ == '__main__':
#     unittest.main()