import json
from flask_restful import abort, request, reqparse, Resource
from jsonschema import validate, SchemaError
from accessors.sample_control_accessor import SampleControlAccessor
from common.dictionary_helper import DictionaryHelper
from common.schemas import Schemas

# Notice there are 2 classes in this file. This is a little different than other languages because of the way
# python works with overriding method signatures.
# Replace later with marshmallow but for now this works

parser = reqparse.RequestParser()
parser.add_argument('type', type=str, required=False)
parser.add_argument('site', type=str, required=False)
parser.add_argument('control_id', type=str, required=False)


class SampleControl(Resource):

    # Good example of sending back 404 "not found"
    def get(self):
        args = parser.parse_args()
        sample_control = SampleControlAccessor().query_sample_controls(args) if DictionaryHelper(args).has_values() \
            else SampleControlAccessor().get_sample_controls()

        return sample_control if sample_control is not None else \
            abort(404, message="No sample controls meet the query parameters")

    # curl -X POST -H "Content-Type: application/json" -d '{ "price":"123", "name":"fork"}' "http://localhost:5000/sample_controls"
    def post(self):
        args = parser.parse_args()
        input_json = request.get_json()
        try:
            validate(input_json, Schemas.get_sequencer_schema())
        except SchemaError, e:
            print e

        if args['control_id'] is not None:
            abort(400, message="Can not create a new sample control if id is passed in")
        elif DictionaryHelper(args).keys_have_value(['type', 'site']):
            return "Yeah, you passed in the correct parameters to create a new sample control"

        abort(400, message="Must send in both a site and a type")
