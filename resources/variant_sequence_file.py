from resources.generic_file import GenericFile
from resource_helpers.abort_logger import AbortLogger
from flask.ext.cors import cross_origin
from resources.auth0_resource import requires_auth

valid_file_formats = ['vcf', 'tsv']


class VariantGenericFile(GenericFile):

    # @cross_origin(headers=['Content-Type', 'Authorization'])
    # @requires_auth
    def get(self, molecular_id, file_format):

        if file_format.lower() in valid_file_formats:
            return self.get_file_url(molecular_id, str(file_format) + "_name")

        AbortLogger.log_and_abort(400, self.logger.error, "Only supports vcf and tsv files")
