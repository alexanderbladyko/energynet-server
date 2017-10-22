from utils.server import register_url
from game.api.auction import auction_bid, auction_pass
from game.api.auction.get import get_auction
from game.api.resources.get import get_resources
from game.api.resources import resources_buy
from game.api.finance import finance_receive
from game.api.game import choose_color
from game.api.game.start import start_game
from game.api.game.info import game_info
from game.api.stations import station_remove
from game.api.cities import cities_buy


class GameRoutes(object):
    def init_routes(self):
        register_url('game_start', start_game, handle_response=True)

        register_url('game', game_info)

        register_url('resources', get_resources, auth_only=True)
        register_url('auction', get_auction)

        register_url('color_choose', choose_color.run, handle_response=True, auth_only=True)  # noqa

        register_url('auction_bid', auction_bid.run, handle_response=True, auth_only=True)  # noqa
        register_url('auction_pass', auction_pass.run, handle_response=True, auth_only=True)  # noqa

        register_url('resource_buy', resources_buy.run, handle_response=True, auth_only=True)  # noqa

        register_url('station_remove', station_remove.run, handle_response=True, auth_only=True)  # noqa

        register_url('cities_buy', cities_buy.run, handle_response=True, auth_only=True)  # noqa

        register_url('finance_receive', finance_receive.run, handle_response=True, auth_only=True)  # noqa
