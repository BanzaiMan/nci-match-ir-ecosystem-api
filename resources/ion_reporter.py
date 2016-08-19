import json
from flask_restful import abort, request, Resource
from accessors.sequencer_file_queue import SequencerFileQueue
from common.schemas import Schemas
from jsonschema import validate, SchemaError

# curl -X POST -H "Content-Type: application/json" -d '{ "molecular_id":"123", "analysis_id":"fork", "patient_id":"fork", "site":"fork", "vcf_file_name":"fork", "dna_bam_file_name":"fork", "cdna_bam_file_name":"fork"}' "http://localhost:5000/ion_reporters"

class IonReporter(Resource):
    def post(self):
<<<<<<< Updated upstream
        input_json = request.get_json()
        try:
            validate(input_json, Schemas.get_sequencer_schema())
            print('Success!, schema is valid')
        except SchemaError, e:
            print('You have a schema error')
            print e
=======
        #Todo: validate
        SequencerFileQueue().write('')



>>>>>>> Stashed changes

        SequencerFileQueue().write(json.dumps(input_json))

<<<<<<< Updated upstream
=======
        #
        # molecular_id: {molecular_id},
        # analysis_id: {analysis_id},
        # site: {site},
        # bucket: {bucket},
        # date_created: {date_created},
        # tsv_file_name: {tsv_file_name},
        # vcf_file_name: {vcf_file_name},
        # dna_bam_file_name: {dna_bam_file_name},
        # cdna_bam_file_name: {cdna_bam_file_name},
        # dna_bai_file_name: {dna_bai_file_name},
        # cdna_bai_file_name: {c}dna_bai_file_name
>>>>>>> Stashed changes
