import logging
from accessors.sample_control_accessor import SampleControlAccessor
from flask_restful import abort, Resource


class SampleControlRecord(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # TODO: Write PUT (Update)
    def put(self, molecular_id):
        pass

    def delete(self, molecular_id):
        self.logger.info("Deleting sample control with id: " + str(molecular_id))
        try:
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
