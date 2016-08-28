import logging
from flask_restful import abort, request, reqparse, Resource

parser = reqparse.RequestParser()
# TODO: Create a means to store, retrieve, delete, and update information about the ion reporters themselves


class IonReporterTable(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get(self):
        abort(500, message="Not yet implemented")

    def post(self):
        abort(500, message="Not yet implemented")

    def put(self):
        abort(500, message="Not yet implemented")

    def delete(self):
        abort(500, message="Not yet implemented")