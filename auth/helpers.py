import functools
import jwt
from flask import request
from flask_socketio import disconnect

from auth.models import User


def get_token():
    return request.args.get('token')


def get_current_user_id():
    auth_token = get_token()
    return User.decode_auth_token(auth_token)


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        try:
            user_id = get_current_user_id()
            return f(user_id, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            disconnect()
        except jwt.InvalidTokenError:
            disconnect()

    return wrapped
