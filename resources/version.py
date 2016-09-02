import logging
from flask_restful import abort, request, Resource

class Version(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get(self):
        return {'version':'1.0'}