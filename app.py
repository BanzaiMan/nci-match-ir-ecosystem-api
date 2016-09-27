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
from resources.variant_sequence_file import VariantSequenceFile
from resources.alignment_sequence_file import AlignmentSequenceFile
from resources.version import Version
from resources.aliquot import Aliquot
from common.environment_helper import EnvironmentHelper


# Boilerplate code to start flask
app = flask.Flask(__name__)
api = flask_restful.Api(app)
cors = flask_cors.CORS(app, resources={r"/api/*": {"origins": "*"}})

# Logging functionality
fileConfig(os.path.abspath("config/logging_config.ini"))
logger = logging.getLogger(__name__)

# Use this variable to read the config file which contains the database connection and
# tier (i.e., development, tests, uat, production) specific configuration information.

EnvironmentHelper.set_environment(logger.info)

# Notice that the class names are singular, but I choose to keep the routes all plural
# this was following a pattern I found on a blog. Its really just a matter of opinion. The goal
# is to make an API consistent for the user. So neither plural nor singular is 'grammatically' correct
# but we pick plural because it tends to be the favored practice for the user, yet we break OO practice by having
# plural classes.

# Path for Querying and Creating sample controls
api.add_resource(SampleControlTable, '/api/v1/sample_controls')

# Path for Updating and deleting a specific sample control
api.add_resource(SampleControlRecord, '/api/v1/sample_controls/<string:identifier>')

# Paths for downloading vcf or tsv file, format = vcf|tsv
api.add_resource(VariantSequenceFile, '/api/v1/sequence_files/<string:molecular_id>/<string:file_format>')
# TODO: still working on this
api.add_resource(S3AuthenticationPolicy,
                 '/api/v1/files/<string:molecular_id>/<string:analysis_id>/<string:file_name>')

# Paths for downloading bam or bai file, format = bam|bai, type=cdna|dna
api.add_resource(AlignmentSequenceFile,
                 '/api/v1/sequence_files/<string:molecular_id>/<string:file_format>/<string:nucleic_acid_type>')

# Paths for updating information about ion reporters themselves
api.add_resource(IonReporterTable, '/api/v1/ion_reporters')
api.add_resource(IonReporterRecord, '/api/v1/ion_reporters/<string:identifier>')
api.add_resource(SequenceData, '/api/v1/ion_reporters/<string:ion_reporter_id>/<string:sequence_data>')

# Path for either sending in files from the ir (bam,vcf) to process them and store them based on their molecular id
# in either the patient or sample_control table. Also a path to query with GET to see if molecular_id is valid and
# what type of molecular id it is (i.e., sample_control or patient)
api.add_resource(Aliquot, '/api/v1/aliquot/<string:molecular_id>')

# Path for version call, returning 200 as test response
api.add_resource(Version, '/api/v1/ion_reporters/version')

# For the most part, this is boilerplate code to start tornado server
if __name__ == '__main__':
    logger.info("server starting on port 5000:")
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port=5000)
    IOLoop.instance().start()

