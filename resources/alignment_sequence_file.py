from resources.sequence_file import SequenceFile


class AlignmentSequenceFile(SequenceFile):

    def get(self, molecular_id, file_format, nucleic_acid_type):
        return self.get_file_url(molecular_id, str(nucleic_acid_type) + "_" + str(file_format) + "_name")
