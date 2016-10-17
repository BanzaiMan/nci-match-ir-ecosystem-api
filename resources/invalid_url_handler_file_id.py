from flask_restful import Resource


class InvalidURLHandlerFileId(Resource):

    @staticmethod
    def get(molecular_id):
        return {'Error': 'The requested URL was not found on the server. Missing file name in URL. Please check usage.'}
