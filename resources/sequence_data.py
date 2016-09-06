import logging
from flask_restful import abort, request, Resource, reqparse
from accessors.celery_task_accessor import CeleryTaskAccessor
from accessors.ion_reporter_accessor import IonReporterAccessor
from accessors.sample_control_accessor import SampleControlAccessor
from common.dictionary_helper import DictionaryHelper

parser = reqparse.RequestParser()

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
                    return [d[str(args['projection'])] for d in sample_controls]
                else:
                    return sample_controls

            except Exception, e:
                self.logger.debug("Ion Reporter ID: " + str(ion_reporter_id) + " was not found in sample control table")
                abort(404, message="Ion Reporter ID not found because " + e.message)

                    # sample_controls = SampleControlAccessor().scan({str(args['projection']): args['projection']})
            #
            #         if sample_controls is not None:
            #             self.logger.debug("Found: sample_controls")
            #             return sample_controls
            #         else:
            #             self.logger.debug(str(args['projection']) +"sample controls was not found in ion reporter table record")
            #             abort(404, message=str(args['projection'] + "sample controls was not found in Ion Reporter Record found because " + e.message)
            #
            # return results['Item']



