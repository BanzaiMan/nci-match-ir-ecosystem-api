from resources.sequence_file import SequenceFile
from resource_helpers.abort_logger import AbortLogger

valid_file_formats = ['bam', 'bai']
valid_nucleic_acid_types = ['cdna', 'dna']


class AlignmentSequenceFile(SequenceFile):

    def get(self, molecular_id, file_format, nucleic_acid_type):
        if (file_format.lower() in valid_file_formats) and (nucleic_acid_type.lower() in valid_nucleic_acid_types):
            return self.get_file_url(molecular_id, str(nucleic_acid_type) + "_" + str(file_format) + "_name")

        AbortLogger.log_and_abort(400, self.logger.error, "Only supports bam|bai and cdna|dna")
