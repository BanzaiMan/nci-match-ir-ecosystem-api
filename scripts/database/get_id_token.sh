#!/usr/bin/env bash

# *******************************************************************
# * Script to run curl commands for retrieving id_token.                       *
# *******************************************************************


id_token= curl -v -H "Content-Type: application/json" -X POST -d '{"client_id":"'"$AUTH0_CLIENT_ID"'","username":"'"$AUTH0_USERNAME"'","password":"'"$AUTH0_PASSWORD"'","grant_type":"password","scope":"openid roles","connection":"'"$AUTH0_DATABASE"'"}' https://ncimatch.auth0.com/oauth/ro
