import logging
import json
import simplejson
import codecs
from flask_restful import Resource
from flask.json import jsonify
from accessors.sample_control_accessor import SampleControlAccessor
from accessors.s3_accessor import S3Accessor
from resource_helpers.abort_logger import AbortLogger
from flask.ext.cors import cross_origin
from resources.auth0_resource import requires_auth


class QualityControl(Resource):
    """This class is for reading QC.json file from s3 and output QC content in json format via API. """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # @cross_origin(headers=['Content-Type', 'Authorization'])
    # @requires_auth
    def get(self, molecular_id):
        # check if molecular_id exists in sample control table
        self.logger.info("Checking if molecular id: " + str(molecular_id) + " is in sample control table")
        try:
            results = SampleControlAccessor().get_item({'molecular_id': molecular_id})
        except Exception as e:
            AbortLogger.log_and_abort(500, self.logger.error, "Failed to get " + molecular_id + " because: " + e.message)
        # results = SampleControlAccessor().get_item({'molecular_id': molecular_id})

        if len(results) > 0:
            self.logger.info("Molecular id: " + str(molecular_id) + " found in sample control table")
            results = json.loads(simplejson.dumps(results, use_decimal=True))
            if not 'tsv_name' in results:
                AbortLogger.log_and_abort(404, self.logger.debug, "tsv file s3 path does not exist. Cannot get qc.json file s3 path for " +str(molecular_id))
            tsv_s3_path = results['tsv_name']
            qc_json_s3_path = tsv_s3_path.replace("tsv", "json")

            self.logger.info("Downloading QC.json file: " + qc_json_s3_path )
            downloaded_file_path = S3Accessor().download(qc_json_s3_path)
            # Rule Engine output QC.json file is encoded by unicode encoder UTF-16
            data = json.loads(codecs.open(downloaded_file_path, 'r', encoding='UTF-16').read())
            return jsonify(data)
        else:
            AbortLogger.log_and_abort(404, self.logger.debug, str(molecular_id + " was not found. Invalid molecular_id or invalid projection key entered."))

