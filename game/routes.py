from utils.server import socketio
from game.api.start import start_game
from game.api.info import game_info


class GameRoutes(object):
    def init_routes(self):
        socketio.on('game_start')(start_game)
        socketio.on('game')(game_info)
