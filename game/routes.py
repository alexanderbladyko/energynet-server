from utils.server import socketio
from game.api.auction import get_auction, auction_bid, auction_pass
from game.api.info import game_info
from game.api.resources import get_resources
from game.api.start import start_game
from game.api.color import choose_color


class GameRoutes(object):
    def init_routes(self):
        socketio.on_event('game_start', start_game)

        socketio.on_event('game', game_info)

        socketio.on_event('resources', get_resources)
        socketio.on_event('auction', get_auction)

        socketio.on_event('color_choose', choose_color)

        socketio.on_event('auction_bid', auction_bid)
        socketio.on_event('auction_pass', auction_pass)
