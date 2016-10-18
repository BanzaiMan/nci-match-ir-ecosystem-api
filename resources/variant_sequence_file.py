from resources.generic_file import GenericFile
from resource_helpers.abort_logger import AbortLogger

valid_file_formats = ['vcf', 'tsv']


class VariantGenericFile(GenericFile):

    def get(self, molecular_id, file_format):

        if file_format.lower() in valid_file_formats:
            return self.get_file_url(molecular_id, str(file_format) + "_name")

        AbortLogger.log_and_abort(400, self.logger.error, "Only supports vcf and tsv files")
