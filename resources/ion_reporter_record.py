import logging
from flask_restful import abort, request, reqparse, Resource

parser = reqparse.RequestParser()
# TODO: Create a means to store, retrieve, delete, and update information about a particular ion reporter


class IonReporterRecord(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # TODO: Besides the querying of the ir table, add ability to get patients and/or sample controls sequenced
    # for more information see https://wiki.nci.nih.gov/display/UM/Ecosystems+Services+and+Tables
    def get(self):
        abort(500, message="Not yet implemented")

    def post(self):
        abort(500, message="Not yet implemented")

    def put(self):
        abort(500, message="Not yet implemented")

    def delete(self):
        abort(500, message="Not yet implemented")