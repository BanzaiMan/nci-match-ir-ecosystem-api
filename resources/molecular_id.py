import logging
from flask_restful import abort, Resource
from accessors.sample_control_accessor import SampleControlAccessor


class MolecularId(Resource):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get(self, molecular_id):
        # 1, Check sample control tables by calling get
        self.logger.info("Checking if molecular id: " + str(molecular_id) + " is in sample control table")
        results = SampleControlAccessor().get_item({'molecular_id': molecular_id})

        if 'Item' in results:
            self.logger.info("Molecular id: " + str(molecular_id) + " found in sample control table")
            item = results['Item'].copy()
            item.update({'molecular_id_type': 'sample_control'})
            return item

        # TODO: Finish the write for the GET molecular_id by calling the patient ecosystem
        # 2. Import requests library and then make a rest call to patient ecosystem to check patient table

        abort(404, message=str(molecular_id + " was not found"))
