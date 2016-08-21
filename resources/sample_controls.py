import logging
from flask_restful import abort, request, reqparse, Resource

from accessors.sample_control_accessor import SampleControlAccessor
from common.dictionary_helper import DictionaryHelper
from common.string_helper import StringHelper

# Notice there are 2 classes in this file. This is a little different than other languages because of the way
# python works with overriding method signatures.
# Replace later with marshmallow but for now this works

parser = reqparse.RequestParser()
parser.add_argument('control_type', type=str, required=False)
parser.add_argument('site', type=str, required=False)
parser.add_argument('molecular_id', type=str, required=False)

MOLECULAR_ID_LENGTH = 5


class SampleControls(Resource):

    """This class is a tiny bit inconsistent by design. The argument types are all optional for the 'GET' but only the
    control_type and site are needed and required for the 'POST.' Passing in any other query parameters to the POST
    will result in an error message being returned. Technically, it would be better to put the post in yet another
    class but  then we end up with 3 classes to handle sample controls (1. One for general queries 'get', 2. One
    for updates 'put, delete' 3. and yet another one for the POST.) That situation, while perfectly consistent with
    REST standards, creates a lot of redudant code. As it is we have 2 sample control classes. This one is named plural,
    which is not really a great naming practice, because it can return 0 or more results for the GET. Obviously,
    on POST it will only create one new sample control but a result of 1 is between 0 and infinity."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get(self):
        self.logger.info("Sample control GET called")
        args = request.args
        self.logger.debug(str(args))
        sample_control = SampleControlAccessor().scan(args) if DictionaryHelper.has_values(args) \
            else SampleControlAccessor().scan(None)

        self.logger.debug(str(sample_control))
        return sample_control if sample_control is not None else \
            abort(404, message="No sample controls meet the query parameters")

    # TODO: DEBUG and finish this POST
    def post(self):
        self.logger.info(StringHelper.generate_molecular_id(MOLECULAR_ID_LENGTH))
        abort(400, message="Must send in both a site and a type")
        # args = request.args
        #
        # if args['molecular_id'] is not None:
        #     abort(400, message="Can not create a new sample control if molecular_id is passed in")
        # elif DictionaryHelper.keys_have_value(['type', 'site']):
        #     return "Yeah, you passed in the correct parameters to create a new sample control"
        #
        # abort(400, message="Must send in both a site and a type")
