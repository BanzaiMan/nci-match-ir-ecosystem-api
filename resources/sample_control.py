import json
import logging
from flask_restful import abort, request, reqparse, Resource
from jsonschema import validate, SchemaError
from accessors.sample_control_accessor import SampleControlAccessor
from common.dictionary_helper import DictionaryHelper
from common.schemas import Schemas

# Notice there are 2 classes in this file. This is a little different than other languages because of the way
# python works with overriding method signatures.
# Replace later with marshmallow but for now this works

parser = reqparse.RequestParser()
parser.add_argument('control_type', type=str, required=False)
parser.add_argument('site', type=str, required=False)
parser.add_argument('molecular_id', type=str, required=False)


class SampleControl(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get(self):
        self.logger.info("Sample control GET called")
        args = request.args
        self.logger.debug(str(args))
        sample_control = SampleControlAccessor().scan(args) if DictionaryHelper(args).has_values() \
            else SampleControlAccessor().scan(None)

        self.logger.debug(str(sample_control))
        return sample_control if sample_control is not None else \
            abort(404, message="No sample controls meet the query parameters")

    # TODO: DEBUG and finish this POST
    def post(self):
        args = request.args

        if args['molecular_id'] is not None:
            abort(400, message="Can not create a new sample control if molecular_id is passed in")
        elif DictionaryHelper(args).keys_have_value(['type', 'site']):
            return "Yeah, you passed in the correct parameters to create a new sample control"

        abort(400, message="Must send in both a site and a type")
