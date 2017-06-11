
import jwt
from flask import jsonify, request

from auth.models import User


def get_user_info():
    response = {}
    auth_token = request.headers.get('Authorization')
    is_authenticated = False
    try:
        user_id = User.decode_auth_token(auth_token)
        is_authenticated = True
    except jwt.ExpiredSignatureError:
        pass
    except jwt.InvalidTokenError:
        pass

    response['isAuthenticated'] = is_authenticated
    response['userToken'] = auth_token

    return jsonify(response)
