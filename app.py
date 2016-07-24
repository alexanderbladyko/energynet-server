from flask import jsonify
from flask_login import LoginManager, current_user, login_required
from flask_socketio import SocketIO
from gevent import monkey

from auth.models import User

from helpers.config import config
from helpers.logger import handler
from helpers.server import app

from routes import init_routes

monkey.patch_all()

game_api = config.get('urls', 'game_api')

io = SocketIO(app)
login_manager = LoginManager()

login_manager.init_app(app)

init_routes()


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


@app.route('%s/test_auth' % game_api)
@login_required
def test_auth_response():
    return 'Hurray, you did it'


@app.route('/config', methods=['GET'])
def get_config():
    host = config.get('app', 'host')
    port = config.get('app', 'port')
    game_api = config.get('urls', 'game_api')
    auth_api = config.get('urls', 'auth_api')
    return jsonify({
        'serverUrl': '%s:%s' % (host, port),
        'gameApi': game_api,
        'authApi': auth_api,
    })


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
