import logging
from accessors.sample_control_accessor import SampleControlAccessor
from flask_restful import abort, Resource

# TODO: Qing, in order to take in query parameters you need to put code here to recieve query parameters. Look at the example in the sample_control_table.py

class SampleControlRecord(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def put(self, molecular_id):
        # TODO: Qing, the caller will not know what the update_expresion, or expression_attribute_values will be. Nor should they because they shouldn't know we are using dynamodb.
        # you need methods that take a dictionary and creates these values. This is what the common.Query Helper class
        # is for.  Recall that the person calling this particular method is just putting in a
        # def put(self, molecular_id, update_expression, expression_attribute_values):
        self.logger.info("updating sample control with id: " + str(molecular_id))
        try:
            # TODO: Instead of writing directly put on queue and then pop off queue to do delete
            # SampleControlAccessor().update_item({'molecular_id': molecular_id}, update_expression,
            #                                   expression_attribute_values)
            return {"message": "Item updated", "molecular_id": molecular_id}
        except Exception, e:
            self.logger.debug("updated_item failed because" + e.message)

    def delete(self, molecular_id):
        self.logger.info("Deleting sample control with id: " + str(molecular_id))
        try:
            # TODO: Instead of writing directly put on queue and then pop off queue to do delete
            SampleControlAccessor().delete_item({'molecular_id': molecular_id})
            return {"message": "Item deleted", "molecular_id": molecular_id}
        except Exception, e:
            self.logger.debug("delete_item failed because" + e.message)

    def get(self, molecular_id):
        self.logger.info("Getting sample control with id: " + str(molecular_id))
        try:
            results = SampleControlAccessor().get_item({'molecular_id': molecular_id})

            if 'Item' in results:
                self.logger.debug("Found: " + str(results['Item']))
                return results['Item']

        except Exception, e:
            self.logger.debug("get_item failed because" + e.message)
            abort(500, message="get_item failed because " + e.message)

        self.logger.info(molecular_id + " was not found")
        abort(404, message=str(molecular_id + " was not found"))
