import logging
from string import Template
from flask_restful import abort, Resource, reqparse
from accessors.sample_control_accessor import SampleControlAccessor
from resource_helpers.abort_logger import AbortLogger

MESSAGE_501 = Template("Finding patients sequenced with IR: $ion_reporter_id not yet implemented.")
MESSAGE_500 = Template("Server Error contact help: $error")
MESSAGE_404 = Template("No sample controls sequenced with id: $ion_reporter_id found")
MESSAGE_400 = Template("Can only request patients or sample_controls. You requested: $sequence_data")

parser = reqparse.RequestParser()
parser.add_argument('projection', type=str, required=False, action='append')


class SequenceData(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get(self, ion_reporter_id, sequence_data):
        self.logger.info("Getting sequence data for ion reporter with id: " + str(ion_reporter_id))
        args = parser.parse_args()

        if sequence_data == 'patients':
            AbortLogger.log_and_abort(501, self.logger.debug, MESSAGE_501.substitute(ion_reporter_id=ion_reporter_id))

        elif sequence_data == 'sample_controls':
            try:
                sample_controls = SampleControlAccessor().scan({'ion_reporter_id': ion_reporter_id})
            except Exception, e:
                AbortLogger.log_and_abort(500, self.logger.error, MESSAGE_500.substitute(error=e.message))
            else:
                if len(sample_controls) > 0:
                    if args['projection'] is not None:
                        return [{str(project): sc[str(project)] for project in args['projection'] if project in sc}
                                for sc in sample_controls]
                    else:
                        return sample_controls

                AbortLogger.log_and_abort(404, self.logger.error, MESSAGE_404.substitute(ion_reporter_id=ion_reporter_id))

        else:
            AbortLogger.log_and_abort(404, self.logger.debug, MESSAGE_400.substitute(sequence_data=sequence_data))
