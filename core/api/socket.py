from flask_login import current_user, AnonymousUserMixin

from utils.server import app
from utils.socket_server import io


def ws_connect():
    # app.logger.info('Somebody connected %s' % request.namespace)
    if current_user.is_authenticated:
        app.logger.info('User %s connected' % current_user.name)
        io.emit('shlyapa', 'test')
    else:
        return None


def ws_disconnect():
    if current_user is not AnonymousUserMixin:
        app.logger.info('User %s disconnected' % current_user.name)
    else:
        app.logger.info('Some anonym is disconnected')


def error_handler(e):
    app.logger.error("Websocket error: %s" % e)


def default_error_handler(e):
    app.logger.error("Unknown websocket error: %s" % e)
