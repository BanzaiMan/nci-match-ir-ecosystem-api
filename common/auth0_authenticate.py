import requests
import __builtin__
import os
import json

class Auth0Authenticate(object):

    @staticmethod

    def get_id_token():
        auth0_url = (__builtin__.environment_config[__builtin__.environment]['auth0_database_url'])
        headers = {'Content-type': 'application/json'}
        content = {
                  "token_type": "bearer",
                  "username": os.environ['AUTH0_USERNAME'],
                  "password": os.environ['AUTH0_PASSWORD'],
                  "connection": os.environ['AUTH0_DATABASE'],
                  "grant_type": "password",
                  "scope": "openid roles",
                  "client_id": os.environ['AUTH0_CLIENT_ID']
                }


        r = requests.post(auth0_url, data=json.dumps(content), headers=headers)
        r_dict = json.loads(r.content)
        id_token = r_dict["id_token"]



        return str(id_token)
        # return str(r.content)
