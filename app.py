import logging
import os
import yaml
import __builtin__
from logging.config import fileConfig
from flask import Flask
from flask_restful import Api
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer
from accessors.sample_control_accessor import SampleControlAccessor

from resources.ion_reporter import IonReporter
from resources.sample_control_table import SampleControlTable
from resources.sample_control_record import SampleControlRecord
from resources.molecular_id import MolecularId

# Boilerplate code to start flask
app = Flask(__name__)
api = Api(app)

# Logging functionality
# TODO: fix path issue to work on multiple OSes
fileConfig('config/logging_config.ini')
logger = logging.getLogger(__name__)

# Use this variable to read the config file which contains the database connection and
# tier (i.e., development, tests, uat, production) specific configuration information.
__builtin__.environment = None
try:
    __builtin__.environment = os.environ['ENVIRONMENT']
except KeyError, e:
    logger.error("Must configure ENVIRONMENT variable in your environment in order for application to start")
    logger.error(e.message)

logger.info("Environment set to: " + __builtin__.environment)

# Use the environment variable from above to read yaml config file and set global variable to the loaded file
# so tier specific information may be retrieved by the various modules as needed.
with open("config/environment.yml", 'r') as yaml_file:
    __builtin__.environment_config = yaml.load(yaml_file)

# Notice that the class names are singular, but I choose to keep the routes all plural
# this was following a pattern I found on a blog. Its really just a matter of opinion. The goal
# is to make an API consistent for the user. So neither plural nor singular is 'grammatically' correct
# but we pick plural because it tends to be the favored practice for the user, yet we break OO practice by having
# plural classes.

# Path for Querying and Creating sample controls
api.add_resource(SampleControlTable, '/v1/sample_controls')

# Path for Updating and Deleting sample controls
api.add_resource(SampleControlRecord, '/v1/sample_controls/<string:molecular_id>')

# Path for updating information about ion reporters themselves
api.add_resource(IonReporter, '/v1/ion_reporters')

# Path for either sending in files from the ir (bam,vcf) to process them and store them based on their molecular id
# in either the patient or sample_control table. Also a path to query with GET to see if molecular_id is valid and
# what type of molecular id it is (i.e., sample_control or patient)
api.add_resource(MolecularId, '/v1/molecular_id/<string:molecular_id>')

# For the most part, this is boilerplate code to start tornado server
if __name__ == '__main__':
    logger.info("server starting on port 5000:")
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port=5000)
    IOLoop.instance().start()

