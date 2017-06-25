import jwt

from flask_socketio import emit

from auth import helpers
from core.logic import ensure_user


def ws_connect():
    try:
        user_id = helpers.get_current_user_id()
        emit('handshake', {
            'id': user_id,
        })
        ensure_user(user_id)
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
