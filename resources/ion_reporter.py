import json
import logging
from flask_restful import abort, request, Resource
from accessors.update_queue_accessor import UpdateQueueAccessor
from common.schemas import Schemas
from jsonschema import validate, ValidationError


# curl -X POST -H "Content-Type: application/json" -d '{ "molecular_id":"123", "analysis_id":"fork",
# "patient_id":"fork", "site":"fork", "vcf_file_name":"fork", "dna_bam_file_name":"fork", "cdna_bam_file_name":"fork"}'
# "http://localhost:5000/ion_reporters"
class IonReporter(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def post(self):

        self.logger.info('New Ion Reporter file names are attempting to be POSTED to SQS queue')
        input_json = request.get_json()
        self.logger.debug(json.dumps(input_json))
        try:
            validate(input_json, Schemas.get_sequencer_schema())
        except ValidationError, e:
            self.logger.error("JSON validation failed: " + e.message)
            abort(400, message="JSON was not valid: " + e.message)

        self.logger.info('JSON validated')
        try:
            # TODO:Change to use celery
            UpdateQueueAccessor().write(json.dumps(input_json))
            self.logger.info('New Ion Reporter file names POSTED to SQS queue')
        except Exception, e:
            self.logger.error("Unable to import message details: " + e.message)
            abort(500, message="Unable to import message details: " + e.message)