import logging
from flask_restful import abort, request, reqparse, Resource
from accessors.ir_accessor import IonReporterAccessor
from common.dictionary_helper import DictionaryHelper

parser = reqparse.RequestParser()
# TODO: Create a means to store, retrieve, delete, and update information about the ion reporters themselves

parser.add_argument('ir_id', type=str, required=False)
parser.add_argument('ip_address', type=str, required=False)
parser.add_argument('internal_ip_address',         type=str, required=False)
parser.add_argument('host_name', type=str, required=False)
parser.add_argument('site', type=str, required=False)
parser.add_argument('status', type=str, required=False)
parser.add_argument('last_contact', type=str, required=False)
parser.add_argument('data_files', type=str, required=False)

class IonReporterTable(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

# TODO begin here WAiO

    def get(self):
        self.logger.info("Ion reporter GET called")
        args = request.args
        self.logger.debug(str(args))
        try:
            ion_reporter = IonReporterAccessor().scan(args) if DictionaryHelper.has_values(args) \
                else IonReporterAccessor().scan(None)
            self.logger.debug(str(ion_reporter))
            return ion_reporter if ion_reporter is not None else \
                abort(404, message="No ion reporters meet the query parameters")
        except Exception, e:
            self.logger.error("Get failed because: " + e.message)
            abort(500, message="Get failed because: " + e.message)


    def post(self):
        abort(500, message="Not yet implemented")

    def put(self):
        abort(500, message="Not yet implemented")

    def delete(self):
        abort(500, message="Not yet implemented")