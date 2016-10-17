from flask_restful import Resource


class InvalidURLHandlerSequenceFileId(Resource):

    # user only pass molecular_id in order to get sequence file, e.g. /api/v1/sequence_files/<string:molecular_id>
    @staticmethod
    def get(molecular_id):
        return {'Error': 'The requested URL was not found on the server. Missing file type in URL. Please check usage.'}
