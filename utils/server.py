from flask import Flask
from flask_socketio import SocketIO

from utils.blueprint import blueprint
from utils.config import config
# from utils.logger import handler
from utils.login_manager import login_manager
from utils.redis import sessions_redis
from utils.sessions import RedisSessionInterface

socketio = SocketIO(engineio_logger=True)


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.get('socketio', 'secret')
    app.debug = config.get('app', 'debug')

    # app.logger.addHandler(handler)

    app.register_blueprint(blueprint)

    # login_manager.init_app(app)

    # app.session_interface = RedisSessionInterface(sessions_redis)

    socketio.init_app(app)

    return app
