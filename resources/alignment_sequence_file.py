from resources.generic_file import GenericFile
from resource_helpers.abort_logger import AbortLogger
from flask.ext.cors import cross_origin
from resources.auth0_resource import requires_auth

valid_file_formats = ['bam', 'bai']
valid_nucleic_acid_types = ['cdna', 'dna']


class AlignmentGenericFile(GenericFile):

    # @cross_origin(headers=['Content-Type', 'Authorization'])
    # @requires_auth
    def get(self, molecular_id, file_format, nucleic_acid_type):
        if (file_format.lower() in valid_file_formats) and (nucleic_acid_type.lower() in valid_nucleic_acid_types):
            return self.get_file_url(molecular_id, str(nucleic_acid_type) + "_" + str(file_format) + "_name")

        AbortLogger.log_and_abort(400, self.logger.error, "Only supports bam|bai and cdna|dna")
