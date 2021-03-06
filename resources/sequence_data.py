import logging
from string import Template
from flask_restful import request, Resource, reqparse
from accessors.sample_control_accessor import SampleControlAccessor
from resource_helpers.abort_logger import AbortLogger
from common.dictionary_helper import DictionaryHelper
from flask.ext.cors import cross_origin
from resources.auth0_resource import requires_auth
from flask.json import jsonify


MESSAGE_501 = Template("Finding patients sequenced with IR: $ion_reporter_id not yet implemented.")
MESSAGE_500 = Template("Server Error contact help: $error")
MESSAGE_404 = Template("No sample controls sequenced with id: $ion_reporter_id found")
MESSAGE_400 = Template("Can only request patients or sample_controls. You requested: $sequence_data")


class SequenceData(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @cross_origin(headers=['Content-Type', 'Authorization'])
    @requires_auth
    def get(self, ion_reporter_id, sequence_data):
        self.logger.info("Getting sequence data for ion reporter with id: " + str(ion_reporter_id) + " sequence_data: "
                         + sequence_data)
        args = request.args
        projection_list, args = DictionaryHelper.get_projection(args)

        if sequence_data == 'patients':
            AbortLogger.log_and_abort(501, self.logger.debug, MESSAGE_501.substitute(ion_reporter_id=ion_reporter_id))

        elif sequence_data == 'sample_controls':
            try:
                sample_controls = SampleControlAccessor().scan({'ion_reporter_id': ion_reporter_id},
                                                               ','.join(projection_list))
            except Exception as e:
                AbortLogger.log_and_abort(500, self.logger.error, MESSAGE_500.substitute(error=e.message))
            else:
                if len(sample_controls) > 0:
                    return jsonify(sample_controls)

                AbortLogger.log_and_abort(404, self.logger.error,
                                          MESSAGE_404.substitute(ion_reporter_id=ion_reporter_id))
        else:
            AbortLogger.log_and_abort(400, self.logger.debug, MESSAGE_400.substitute(sequence_data=sequence_data))
