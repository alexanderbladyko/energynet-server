from utils.server import register_url
from game.api.auction import get_auction, auction_bid, auction_pass
from game.api.info import game_info
from game.api.resources import get_resources, resource_buy
from game.api.start import start_game
from game.api.color import choose_color
from game.api.stations import station_remove
from game.api.cities import cities_buy
from game.api.finance import finance_receive


class GameRoutes(object):
    def init_routes(self):
        register_url('game_start', start_game, handle_response=True)

        register_url('game', game_info)

        register_url('resources', get_resources)
        register_url('auction', get_auction)

        register_url('color_choose', choose_color, handle_response=True)

        register_url('auction_bid', auction_bid, handle_response=True)
        register_url('auction_pass', auction_pass, handle_response=True)

        register_url('resource_buy', resource_buy, handle_response=True)

        register_url('station_remove', station_remove, handle_response=True)

        register_url('cities_buy', cities_buy, handle_response=True)

        register_url('finance_receive', finance_receive, handle_response=True)
