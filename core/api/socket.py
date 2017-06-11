import jwt

from flask import request
from flask_socketio import emit

from auth.models import User
from core.logic import ensure_user


def ws_connect():
    auth_token = request.args.get('token')
    try:
        user_id = User.decode_auth_token(auth_token)
        emit('handshake', {
            'id': user_id,
        })
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def ws_disconnect():
    pass
    # if current_user == AnonymousUserMixin:
        # app.logger.error('Some anonymous is disconnected')
    # else:
        # app.logger.error('User disconnected')


def error_handler(e):
    pass
    # app.logger.error("Websocket error: %s" % e)


def default_error_handler(e):
    pass
    # app.logger.error("Unknown websocket error: %s" % e)
