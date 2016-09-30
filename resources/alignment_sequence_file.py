from resources.sequence_file import SequenceFile
from resource_helpers.abort_logger import AbortLogger


class AlignmentSequenceFile(SequenceFile):

    def get(self, molecular_id, file_format, nucleic_acid_type):
        if (file_format.lower() == 'bam' or file_format.lower() == 'bai') and \
                (nucleic_acid_type.lower() == 'cdna' or nucleic_acid_type.lower() == 'dna'):
            return self.get_file_url(molecular_id, str(nucleic_acid_type) + "_" + str(file_format) + "_name")

        AbortLogger.log_and_abort(400, self.logger.error, "Only supports bam|bai and cdna|dna")
