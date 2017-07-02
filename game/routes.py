from utils.server import socketio
from game.api.auction import get_auction
from game.api.info import game_info
from game.api.resources import get_resources
from game.api.start import start_game
from game.api.color import choose_color


class GameRoutes(object):
    def init_routes(self):
        socketio.on('game_start')(start_game)

        socketio.on('game')(game_info)

        socketio.on('resources')(get_resources)
        socketio.on('auction')(get_auction)

        socketio.on('color_choose')(choose_color)
