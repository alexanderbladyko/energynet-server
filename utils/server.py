from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

from auth.helpers import authenticated_only
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


def register_url(url, handler, handle_response=False, auth_only=False):
    func = handler
    if handle_response:
        func = game_response(url)(func)
    if auth_only:
        func = authenticated_only(func)
    socketio.on_event(url, func)
