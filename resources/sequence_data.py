import logging
from string import Template
from flask_restful import abort, Resource, reqparse
from accessors.sample_control_accessor import SampleControlAccessor

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
            self.logger.debug(MESSAGE_501.substitute(ion_reporter_id=ion_reporter_id))
            abort(501, message=MESSAGE_501.substitute(ion_reporter_id=ion_reporter_id))

        elif sequence_data == 'sample_controls':
            try:
                sample_controls = SampleControlAccessor().scan({'ion_reporter_id': ion_reporter_id})
            except Exception, e:
                self.logger.error(MESSAGE_500.substitute(error=e.message))
                abort(500, message=MESSAGE_500.substitute(error=e.message))
            else:
                if len(sample_controls) > 0:
                    if args['projection'] is not None:
                        return [{str(project): sc[str(project)] for project in args['projection'] if project in sc}
                                for sc in sample_controls]
                    else:
                        return sample_controls

                self.logger.debug(MESSAGE_404.substitute(ion_reporter_id=ion_reporter_id))
                abort(404, message=MESSAGE_404.substitute(ion_reporter_id=ion_reporter_id))

        else:
            self.logger.debug(MESSAGE_400.substitute(sequence_data=sequence_data))
            abort(400, message=MESSAGE_400.substitute(sequence_data=sequence_data))
