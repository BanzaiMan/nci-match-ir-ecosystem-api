import logging
from flask_restful import abort, request, reqparse, Resource


class MolecularId(Resource):

    def __init(self):
        self.logger = logging.getLogger(__name__)

    # TODO: Write the GET molecular_id
    def get(self, molecular_id):
        # 1, Check sample control tables by calling get
        # 2. Import requests and then make a rest call to patient ecosystem to check patient table
        pass
