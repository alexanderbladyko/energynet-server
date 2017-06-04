from flask_socketio import SocketIO
from utils.server import app

io = SocketIO(app, engineio_logger=True)
