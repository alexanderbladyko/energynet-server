from flask import Flask
from flask_socketio import SocketIO

from utils.blueprint import blueprint
from utils.config import config

socketio = SocketIO(engineio_logger=True)


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.get('socketio', 'secret')
    app.debug = config.get('app', 'debug')

    app.register_blueprint(blueprint)

    socketio.init_app(app)

    return app
