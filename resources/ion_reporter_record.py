import logging
from flask_restful import abort, request, Resource, reqparse
from accessors.celery_task_accessor import CeleryTaskAccessor
from accessors.ion_reporter_accessor import IonReporterAccessor
from accessors.sample_control_accessor import SampleControlAccessor
from common.dictionary_helper import DictionaryHelper

parser = reqparse.RequestParser()

parser.add_argument('sample_controls',       type=str, required=False)
parser.add_argument('projection',            type=str, required=False)

class IonReporterRecord(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get(self, ion_reporter_id):
        self.logger.info("Getting ion reporter with id: " + str(ion_reporter_id))
        args = parser.parse_args()
        lower_case_args= dict((k.lower(), v.lower()) for k, v in args.iteritems())
        self.logger.debug("LOWERCASE" + str(lower_case_args))
        try:
            results = IonReporterAccessor().get_item({'ion_reporter_id': ion_reporter_id})

            if 'Item' in results:
                self.logger.debug("Found: " + str(results['Item']))

        except Exception, e:
            self.logger.debug("Ion Reporter ID" + str(ion_reporter_id) + "was not found in ion reporter table")
            abort(404, message="Ion Reporter ID not found because " + e.message)
        lower_case_args = dict((k.lower(), v.lower()) for k, v in args.iteritems())
        self.logger.debug("LOWERCASE" + str(lower_case_args))
        if lower_case_args['sample_controls'] == 'true':
            # What if site was not in results?
            try:
                site = results['Item']['site']
            except Exception, e:
                self.logger.debug("Site was not found in ion reporter table record")
                abort(404, message="Site was not found in Ion Reporter Record found because " + e.message)


            try:
                sample_controls = SampleControlAccessor().scan({'site': site})
                if 'Item' in sample_controls:
                    self.logger.debug("Found: " + str(sample_controls['Item']))
                else:
                    self.logger.debug("Site was not found in ion reporter table record")
                    abort(404, message="Site was not found in Ion Reporter Record found because " + e.message)
                if lower_case_args['projection'] == 'molecular_id':
                    self.logger.debug("Returning molecular ids only")
                    # TODO: I'm surprised this would work... can you show this to me?
                    return [d['molecular_id'] for d in sample_controls]
            except Exception, e:
                self.logger.debug("Site" + str(site) + "was not found in sample controls table" + e.message)
                abort(404, message=str(str(site) + " was not found"))

            self.logger.debug("Attempting to return: all sample controls")
            return sample_controls
        else:
            return results['Item']


    def put(self, ion_reporter_id):
        self.logger.info("updating ion reporter with id: " + str(ion_reporter_id))
        args = request.json
        self.logger.debug(str(args))

        if not DictionaryHelper.has_values(args):
            self.logger.debug("Update item failed, because data to update item with was not passed in request")
            abort(400, message="Update item failed, because data to update item with was not passed in request")

        item_dictionary = args.copy()
        item_dictionary.update({'ion_reporter_id': ion_reporter_id})

        # Very important line of code this takes all of the 'None' values out of the dictionary.
        # Without this, the record would update all attributes in the params above with 'None' unless they
        # were explicitly passed in. In reality, we only want to update the attributes that have been explicitly
        # passed in from the params. If they haven't been passed in then they shouldn't be updated.
        item_dictionary = dict((k, v) for k, v in item_dictionary.iteritems() if v)
        try:
            CeleryTaskAccessor().update_ir_item(item_dictionary)
            # IonReporterAccessor().update(item_dictionary)
        except Exception, e:
            self.logger.debug("updated_item failed because" + e.message)
            abort(500, message="Update item failed, because " + e.message)

        return {"message": "Ion reporter with ion reporter id: " + ion_reporter_id + " updated"}

    def delete(self, ion_reporter_id):
        self.logger.info("Deleting ion reporter with id: " + str(ion_reporter_id))
        try:
            CeleryTaskAccessor().delete_ir_item({'ion_reporter_id': ion_reporter_id})
            return {"message": "Item deleted", "ion_reporter_id": ion_reporter_id}
        except Exception, e:
            self.logger.debug("delete_item failed because" + e.message)
            abort(500, message="delete_item item failed, because " + e.message)