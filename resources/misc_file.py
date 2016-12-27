from resources.generic_file import GenericFile
from flask.ext.cors import cross_origin
from resources.auth0_resource import requires_auth

class MiscFile(GenericFile):

    @cross_origin(headers=['Content-Type', 'Authorization'])
    @requires_auth
    def get(self, molecular_id, file_name):
        return self.get_file_url(molecular_id, str(file_name))
