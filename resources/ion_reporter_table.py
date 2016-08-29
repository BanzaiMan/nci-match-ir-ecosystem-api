import logging
from flask_restful import abort, request, reqparse, Resource
from accessors.ion_reporter_accessor import IonReporterAccessor
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
        self.logger.info("POST Request to create a new ion reporter record")
        args = request.args
        self.logger.debug(str(args))

        if 'ir_id' in args:
            self.logger.debug("Ion reporter creation failed, because ir_id was passed in request")
            abort(400, message="ir_id is not a valid input when attempting to create a new ion reporter record. "
                               "The post will create the id for you. Simply pass in site and ip_address'")

        if DictionaryHelper.keys_have_value(args, ['ip_address', 'site']):
            self.logger.debug("Ion reporter record creation failed, because request ir_id was passed in")

            new_item_dictionary = args.copy()
            new_item_dictionary.update({'ir_id': self.__get_unique_key(),
                                        'date_ir_id_created': str(datetime.datetime.utcnow())})

            self.logger.debug("Attempting to write: " + str(new_item_dictionary))
            try:
                # This should go directly to database do not use queue here...every other write...but not this one.
                # "Put" is correct in this case as dynamodb uses put to mean create. Even though rest uses PUT for
                # updates and POST for creation, typically. Granted in rest a put could be a creation also...but not in
                # our case.
                SampleControlAccessor().put_item(new_item_dictionary)
                return {"result": "New sample control created", "molecular_id": new_item_dictionary['molecular_id']}
            except Exception, e:
                self.logger.error("Could not put_item because " + e.message)
                abort(500, message="put_item failed because " + e.message)

        else:
            self.logger.debug("Sample Control creation failed, because both site and control_type were not passed in")
            abort(400, message="Must send in both a site and a control_type in order to create a sample control")

    def put(self):
        abort(500, message="Not yet implemented")

    def delete(self):
        abort(500, message="Not yet implemented")