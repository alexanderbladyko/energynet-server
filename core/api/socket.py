from flask_login import current_user, AnonymousUserMixin
from flask_socketio import emit

from games.models import User
from utils.server import app


def ws_connect():
    if current_user.is_authenticated:
        app.logger.info(
            'User (%s, %s) connected' % (current_user.id, current_user.name)
        )
        User.ensure()
    else:
        return None


def ws_disconnect():
    if not isinstance(current_user, AnonymousUserMixin):
        app.logger.info('User %s disconnected' % current_user.name)
    else:
        app.logger.info('Some anonym is disconnected')


def error_handler(e):
    app.logger.error("Websocket error: %s" % e)


def default_error_handler(e):
    app.logger.error("Unknown websocket error: %s" % e)
