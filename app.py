from flask import Flask, flash, request, jsonify
from flask_login import LoginManager
from flask_socketio import SocketIO
from gevent import monkey

from auth.models import User

from helpers.config import config

monkey.patch_all()

app = Flask(__name__)
app.config['SECRET_KEY'] = config.get('socketio', 'secret')
app.debug = config.get('app', 'debug')

io = SocketIO(app)
login_manager = LoginManager()

login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    return 'login_form'


@app.route('/config.json', methods=['GET'])
def get_config():
    host = config.get('app', 'host')
    port = config.get('app', 'port')
    game_api = config.get('urls', 'game_api')
    return jsonify({
        'server_url': '%s:%s' % (host, port),
        'game_api': game_api,
    })


@io.on('connect')
def ws_connect():
    flash('Somebody connected %s' % request.namespace)
    io.emit('msg', {'test': 'test'})


@io.on('disconnect')
def ws_disconnect():
    flash('Somebody disconnected %s' % request.namespace)


if __name__ == '__main__':
    port = int(config.get('app', 'port'))

    print('Running at port: %s' % port)
    io.run(app, '0.0.0.0', port=port)
