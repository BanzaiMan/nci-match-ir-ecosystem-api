import logging
from flask_restful import abort, request, Resource
from flask import Response

class Version(Resource):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get(self):
        resp = Response(status=200)
        resp.headers['Version'] = '1.0'
        return resp