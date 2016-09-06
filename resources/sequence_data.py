import logging
from flask_restful import abort, Resource, reqparse
from accessors.ion_reporter_accessor import IonReporterAccessor
from accessors.sample_control_accessor import SampleControlAccessor


parser = reqparse.RequestParser()


# action = append, variable will be in list format
parser.add_argument('projection',       type=str, required=False)


class SequenceData(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get(self, ion_reporter_id, sequence_data):
        self.logger.info("Getting sequence data for ion reporter with id: " + str(ion_reporter_id))
        args = parser.parse_args()

        try:
            results = IonReporterAccessor().get_item({'ion_reporter_id': ion_reporter_id})

            if 'Item' in results:
                self.logger.debug("Found: " + str(results['Item']))

        except Exception, e:
            self.logger.debug("Ion Reporter ID" + str(ion_reporter_id) + "was not found in ion reporter table")
            abort(404, message="Ion Reporter ID not found because " + e.message)

        if sequence_data == 'patients':
            return 'Not yet implemented'

        if sequence_data == 'sample_controls':
            try:
                sample_controls = SampleControlAccessor().scan({'ion_reporter_id': ion_reporter_id})
                if 'Item' in sample_controls:
                    self.logger.debug("Found: " + str(sample_controls['Item']))

                if args['projection'] is not None:
                    # return list of dictionaries instead of list of strings
                    # extract key value pairs of projection and its values from list of dictionaries
                    list_1 = []

                    for sc in sample_controls:
                        if args['projection'] in sc:
                            dictionary_1 = {args['projection']: sc[args['projection']]}
                            list_1.append(dictionary_1)
                    return list_1
                else:
                    return sample_controls

            except Exception, e:
                self.logger.debug("Ion Reporter ID: " + str(ion_reporter_id) + " was not found in sample control table")
                abort(404, message="Ion Reporter ID not found because " + e.message)


