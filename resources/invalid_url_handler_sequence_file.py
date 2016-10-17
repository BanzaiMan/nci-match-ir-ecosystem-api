from flask_restful import Resource


class InvalidURLHandlerSequenceFile(Resource):

    @staticmethod
    def get():
        return {'Error': 'The requested URL was not found on the server. Missing molecular_id and file type in URL. Please check usage.'}
