import json
import logging
from flask_restful import abort, request, reqparse, Resource
from accessors.update_queue_accessor import UpdateQueueAccessor
from common.schemas import Schemas
from jsonschema import validate, ValidationError
from accessors.celery_task_accessor import CeleryTaskAccessor

parser = reqparse.RequestParser()

# TODO: lower priority, but could expand to consider more of the attributes
parser.add_argument('analysis_id', type=str, required=False)
parser.add_argument('site',         type=str, required=False)


# curl -X POST -H "Content-Type: application/json" -d '{ "molecular_id":"123", "analysis_id":"fork",
# "patient_id":"fork", "site":"fork", "vcf_file_name":"fork", "dna_bam_file_name":"fork", "cdna_bam_file_name":"fork"}'
# "http://localhost:5000/ion_reporters/SC_SCA14"
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
            # TODO: Change to celery ir put message to update database only...don't process any files here
            # UpdateQueueAccessor().write(json.dumps(input_json))
            # CeleryTaskAccessor().message_body_item(json.dumps(input_json))
            self.logger.info('New Ion Reporter file names POSTED to SQS queue')
        except Exception, e:
            self.logger.error("Unable to import message details: " + e.message)
            abort(500, message="Unable to import message details: " + e.message)