import requests
import __builtin__
import os
import json

from flask_restful import Resource
from flask.ext.cors import cross_origin
from resources.auth0_resource import requires_auth

class Auth0Authenticate(object):

    @staticmethod
    # @cross_origin(headers=['Content-Type', 'Authorization'])
    # @cross_origin(headers=['Access-Control-Allow-Origin', '*'])
    # @requires_auth
    def get_id_token():
        auth0_url = (__builtin__.environment_config[__builtin__.environment]['database_auth0_url'])
        headers = {'Content-type': 'application/json'}
        content = {
                  "token_type": "bearer",
                  "username": os.environ['AUTH0_USERNAME'],
                  "password": os.environ['AUTH0_PASSWORD'],
                  "connection": "MATCH-Development",
                  "grant_type": "password",
                  "scope": "openid",
                  "client_id": os.environ['AUTH0_CLIENT_ID']
                }


        r = requests.post(auth0_url, data=json.dumps(content), headers=headers)
        r_dict = json.loads(r.content)
        id_token = r_dict["id_token"]


        return str(id_token)
        # return str(r.content)
