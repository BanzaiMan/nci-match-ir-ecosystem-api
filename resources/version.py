from flask_restful import Resource
import urllib
import os

class Version(Resource):

    @staticmethod
    def get():
        page = urllib.urlopen(os.path.abspath("build_number.html")).read()
        return page