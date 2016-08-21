import logging
from logging.config import fileConfig
from flask import Flask
from flask_restful import Api
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer

from resources.ion_reporter import IonReporter
from resources.sample_control_table import SampleControlTable
from resources.sample_control_record import SampleControlRecord

app = Flask(__name__)
api = Api(app)

# Logging functionality
# TODO:fix path issue to work on multiple OSes
fileConfig('config/logging_config.ini')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Notice that the class names are single or plural, but I choose to keep the routes all plural
# this was following a pattern I found on a blog. Its really just a matter of opinion. The goal
# is to make an API consistent for the user. So neither plural nor singular is 'grammatically' correct
# but we pick plural because it tends to be the favored practice for the user, yet we break OO practice by having
# plural classes.

# Path for Querying and Creating Sample Controls
api.add_resource(SampleControlTable, '/sample_controls')

# Path for Updating and Deleting (marking as deleted) Sample controls
api.add_resource(SampleControlRecord, '/sample_controls/<string:molecular_id>')

api.add_resource(IonReporter, '/ion_reporters')
api.add_resource(MolecularId, '/molecular_id')

if __name__ == '__main__':
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port=5000)
    IOLoop.instance().start()
