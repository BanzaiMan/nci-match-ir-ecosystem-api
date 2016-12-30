import jwt
import os
import base64

from functools import wraps
from flask_restful import Resource
from flask import request, jsonify, _request_ctx_stack
from werkzeug.local import LocalProxy

# Authentication annotation
current_user = LocalProxy(lambda: _request_ctx_stack.top.current_user)


# Authentication attribute/annotation
def authenticate(error):
  response = jsonify(error)
  response.status_code = 401
  return response


def requires_auth(function):
  if os.environ['ENVIRONMENT'] == 'development' or os.environ['UNITTEST']== 'true':
    return function
  @wraps(function)
  def decorated(*args, **kwargs):
    auth = request.headers.get('Authorization', None)
    if not auth:
      return authenticate({'code': 'authorization_header_missing', 'description': 'Authorization header is expected'})

    parts = auth.split()

    if parts[0].lower() != 'bearer':
      return {'code': 'invalid_header', 'description': 'Authorization header must start with Bearer'}
    elif len(parts) == 1:
      return {'code': 'invalid_header', 'description': 'Token not found'}
    elif len(parts) > 2:
      return {'code': 'invalid_header', 'description': 'Authorization header must be Bearer + \s + token'}
    token = parts[1]
    auth0_client_secret = base64.b64decode(os.environ['AUTH0_CLIENT_SECRET'].replace("_", "/").replace("-", "+"))
    auth0_client_id = os.environ['AUTH0_CLIENT_ID']
    try:
        payload = jwt.decode(token, auth0_client_secret, audience=auth0_client_id)
    except jwt.ExpiredSignature:
        return authenticate({'code': 'token_expired', 'description': 'token is expired'})
    except jwt.InvalidAudienceError:
        return authenticate({'code': 'invalid_audience', 'description': 'incorrect audience, expected: ' + auth0_client_id })
    except jwt.DecodeError:
        return authenticate({'code': 'token_invalid_signature', 'description': 'token signature is invalid'})

    _request_ctx_stack.top.current_user = user = payload
    return function(*args, **kwargs)
  return decorated


class Auth0Resource(Resource):
    method_decorators = [requires_auth]
