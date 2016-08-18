from flask_restful import abort, reqparse, Resource
from accessors.sequencer_file_queue import SequencerFileQueue

# parser = reqparse.RequestParser()
# parser.add_argument('molecular_id', type=str, required=False)
# parser.add_argument('analysis_id', type=str, required=False)
# parser.add_argument('site', type=str, required=False)
# parser.add_argument('control_id', type=str, required=False)


class IonReporter(Resource):
    def post(self):
        SequencerFileQueue().write('')





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