import logging
import os
import flask_cors
import flask_restful
import flask

from logging.config import fileConfig
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer

from resources.s3_authentication_policy import S3AuthenticationPolicy
from resources.ion_reporter_table import IonReporterTable
from resources.ion_reporter_record import IonReporterRecord
from resources.sequence_data import SequenceData
from resources.sample_control_table import SampleControlTable
from resources.sample_control_record import SampleControlRecord
from resources.variant_sequence_file import VariantGenericFile
from resources.alignment_sequence_file import AlignmentGenericFile
from resources.version import Version
from resources.aliquot import Aliquot
from resources.misc_file import MiscFile
from common.environment_helper import EnvironmentHelper


# Boilerplate code to start flask
app = flask.Flask(__name__)
api = flask_restful.Api(app)
# Very important for development as this stands for Cross Origin Resource sharing. Essentially this is what allows for
# the UI to be run on the same box as this middleware piece of code. Consider this code boiler plate.
cors = flask_cors.CORS(app, resources={r"/api/*": {"origins": "*"}})

# Logging functionality
fileConfig(os.path.abspath("config/logging_config.ini"))
logger = logging.getLogger(__name__)

# Use this class to read the config file which contains the database connection and
# tier (i.e., development, tests, uat, production) specific configuration information.
EnvironmentHelper.set_environment(logger.info)

# Notice that the class names are singular, but I choose to keep the routes all plural
# this was following a pattern I found on a blog. Its really just a matter of opinion. The goal
# is to make an API consistent for the user. So neither plural nor singular is 'grammatically' correct
# but we pick plural because it tends to be the favored practice for the user, yet we break OO practice by having
# plural classes so classes are all singular because they are a single instance.

# Path for Querying and Creating sample controls
# Delete and Put in batch must do those using specific IDs, not allowed here
api.add_resource(SampleControlTable, '/api/v1/sample_controls')

# Path for Updating, deleting, and retrieving a specific sample control
api.add_resource(SampleControlRecord, '/api/v1/sample_controls/<string:identifier>')

# Paths for downloading vcf or tsv file, file_format = vcf|tsv
api.add_resource(VariantGenericFile, '/api/v1/sequence_files/<string:molecular_id>/<string:file_format>')
# Paths for downloading bam or bai file, file_format = bam|bai, nucleic_acid_type=cdna|dna
api.add_resource(AlignmentGenericFile,
                 '/api/v1/sequence_files/<string:molecular_id>/<string:file_format>/<string:nucleic_acid_type>')

# This is to download misc files associated with an aliquot such as the pdf or text files etc. The assumption is that
# the user knows how the record is stored in dynamodb...so file_name must be equal to the dynamodb attribute that
# contains the full path and name of the file to be downloaded. The user can query the aliquot by doing a get to
# retrieve the record they want then once they see the attribute with the file name use that to make this call to
# actually retrieve the file. The dynamodb attribute == file_name
# TODO: Somebody and test this
api.add_resource(MiscFile, '/api/v1/files/<string:molecular_id>/<string:file_name>')

# TODO: still working on this but this will be used to authenticate a user to upload to S3
api.add_resource(S3AuthenticationPolicy,
                 '/api/v1/files/<string:molecular_id>/<string:analysis_id>/<string:file_name>')

# Path for Querying and Creating ion reporters
# Delete and Put in batch must do those using specific IDs, not allowed here
api.add_resource(IonReporterTable, '/api/v1/ion_reporters')
# Paths for updating, deleting, and retrieving information about ion reporters themselves
api.add_resource(IonReporterRecord, '/api/v1/ion_reporters/<string:identifier>')
# Retrieves a list of all the patients or sample_controls sequenced on the given IR reporter
api.add_resource(SequenceData, '/api/v1/ion_reporters/<string:ion_reporter_id>/<string:sequence_data>')

# Path for version call, returning 200 as test response
api.add_resource(Version, '/api/v1/ion_reporters/version')

# Path for getting information about an aliquot (essentially because the user doesn't know if its a patient or sample
# control). So it is the path for querying with GET to see if  molecular_id is valid and what type of molecular id it
# is (i.e., sample_control or patient). Or it could be used for sending (PUT) in file paths from the ir (bam,vcf) to
# process them by pulling the files based on the path passed in, down from s3 and store the new files (TSV or BAI) to
# s3 and these new paths to DynamoDB, based on  their molecular id, in either the patient or sample_control table.
api.add_resource(Aliquot, '/api/v1/aliquot/<string:molecular_id>')

# For the most part, this is boilerplate code to start tornado server
if __name__ == '__main__':
    logger.info("server starting on port 5000:")
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port=5000)
    IOLoop.instance().start()

