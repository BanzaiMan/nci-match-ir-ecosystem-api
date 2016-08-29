import logging
from flask_restful import abort, request, reqparse, Resource

parser = reqparse.RequestParser()
# TODO: Create a means to store, retrieve, delete, and update information about the ion reporters themselves

parser.add_argument('ir_id', type=str, required=False)
parser.add_argument('ip_address', type=str, required=False)
parser.add_argument('internal_ip_address',         type=str, required=False)
parser.add_argument('host_name',         type=str, required=False)
parser.add_argument('site',         type=str, required=False)
parser.add_argument('status',         type=str, required=False)
parser.add_argument('last_contact',         type=str, required=False)
parser.add_argument('data_files',         type=str, required=False)

class IonReporterTable(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

# TODO begin here WAiO

    def get(self):

            abort(500, message="Get failed because: " + e.message)


    def post(self):
        abort(500, message="Not yet implemented")

    def put(self):
        abort(500, message="Not yet implemented")

    def delete(self):
        abort(500, message="Not yet implemented")