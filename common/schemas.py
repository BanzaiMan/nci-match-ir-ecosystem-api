class Schemas(object):

    @staticmethod
    def get_sequencer_schema():
        return {
            "type": "object",
            "properties": {
                "molecular_id": {"type": "string"},
                "analysis_id": {"type": "string"},
                "patient_id": {"type": "string"},
                "site": {"type": "string"},
                "vcf_file_name": {"type": "string"},
                "dna_bam_file_name": {"type": "string"},
                "cdna_bam_file_name": {"type": "string"}
            }
        }
