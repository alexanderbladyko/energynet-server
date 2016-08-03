from flask import jsonify
from flask_login import current_user, login_required
from gevent import monkey

from utils.config import config
from utils.logger import handler
from utils.server import app
from utils.socket_server import io
import utils.login_manager

from routes import init_routes

monkey.patch_all()

game_api = config.get('urls', 'game_api')

init_routes()


@app.route('{0}/user_info'.format(game_api))
def get_user_info():
    response = {}
    response['isAuthenticated'] = current_user.is_authenticated
    if current_user.is_authenticated:
        response['username'] = current_user.username

    return jsonify(response)


@io.on('connect')
def ws_connect():
    # app.logger.info('Somebody connected %s' % request.namespace)
    if current_user.is_authenticated:
        app.logger.info('User %s connected' % current_user.username)
        io.emit('shlyapa', 'test')
    else:
        return None


@io.on('disconnect')
def ws_disconnect():
    app.logger.info('User %s disconnected' % current_user.username)


@io.on_error()
def error_handler(e):
    app.logger.error("Websocket error: %s" % e)


@io.on_error_default
def default_error_handler(e):
    app.logger.error("Unknown websocket error: %s" % e)


if __name__ == '__main__':
    port = int(config.get('app', 'port'))

    app.logger.addHandler(handler)
    print('Running at port: %s' % port)
    io.run(app, '0.0.0.0', port=port)
