from flask_restful import Resource
import os
import webbrowser


class Version(Resource):

    @staticmethod
    def get():
        filename = os.path.abspath("build_number.html")
        webbrowser.open_new_tab(filename)
        return {'version': '1.0'}
