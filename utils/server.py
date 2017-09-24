from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

from base.decorators import game_response
from utils.blueprint import blueprint
from utils.config import config
from utils.logger import handler

socketio = SocketIO(engineio_logger=True)


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.get('socketio', 'secret')
    app.debug = config.get('app', 'debug')

    CORS(app, resources={r'/*': {'origins': '*'}})

    app.register_blueprint(blueprint)
    app.logger.addHandler(handler)

    socketio.init_app(app)

    return app


def register_url(url, handler, handle_response=False):
    if handle_response:
        socketio.on_event(url, game_response(url)(handler))
    else:
        socketio.on_event(url, handler)
