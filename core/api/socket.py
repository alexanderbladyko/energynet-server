import jwt

from flask_socketio import emit

from auth import helpers
from core.logic import ensure_user

import structlog
logger = structlog.get_logger()


def ws_connect():
    try:
        user_id = helpers.get_current_user_id()
        emit('handshake', {
            'id': user_id,
        })
        ensure_user(user_id)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def error_handler(e):
    logger.error('WebsocketError', exception=e)


def default_error_handler(e):
    logger.error('UnknownWebsocketError', exception=e)
