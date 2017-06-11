import functools
import jwt
from flask import request
from flask_socketio import disconnect

from auth.models import User


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        auth_token = request.args.get('token')
        try:
            user_id = User.decode_auth_token(auth_token)
            return f(user_id, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            disconnect()
        except jwt.InvalidTokenError:
            disconnect()

    return wrapped
