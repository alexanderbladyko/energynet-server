from flask_login import current_user, AnonymousUserMixin
from flask_socketio import emit

from core.logic import ensure_user
from utils.server import app


def ws_connect():
    if current_user.is_authenticated:
        app.logger.error(
            'User (%s, %s) connected' % (current_user.id, current_user.name)
        )
        emit('handshake', 'connected')
        ensure_user(current_user)
    else:
        return None


def ws_disconnect():
    if current_user == AnonymousUserMixin:
        app.logger.error('Some anonymous is disconnected')
    else:
        app.logger.error('User disconnected')


def error_handler(e):
    app.logger.error("Websocket error: %s" % e)


def default_error_handler(e):
    app.logger.error("Unknown websocket error: %s" % e)
