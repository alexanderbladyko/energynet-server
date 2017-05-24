from utils.socket_server import io
from game.api.start import start_game


class GameRoutes(object):
    def init_routes(self):
        io.on('start')(start_game)
