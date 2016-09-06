import logging
from flask_restful import Resource


class Version(Resource):

    @staticmethod
    def get():
        return {'version': '1.0'}
