from utils.server import socketio
from game.api.start import start_game


class GameRoutes(object):
    def init_routes(self):
        socketio.on('start')(start_game)
