from resources.sequence_file import SequenceFile


class VariantSequenceFile(SequenceFile):

    def get(self, molecular_id, file_format):
        return self.get_file_url(molecular_id, str(file_format) + "_name")
