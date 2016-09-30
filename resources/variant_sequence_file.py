from resources.sequence_file import SequenceFile
from resource_helpers.abort_logger import AbortLogger


class VariantSequenceFile(SequenceFile):

    def get(self, molecular_id, file_format):
        if file_format.lower() == 'vcf' or file_format.lower() == 'tsv':
            return self.get_file_url(molecular_id, str(file_format) + "_name")

        AbortLogger.log_and_abort(400, self.logger.error, "Only supports vcf and tsv files")
