from utils.server import register_url
from games.api.find import find_game
from games.api.list import get_list
from games.api.new import create_new
from games.api.join import join_lobby
from games.api.lobby import send_lobby_info
from games.api.leave import leave_lobby


class GamesRoutes(object):
    def init_routes(self):
        register_url('games', find_game)
        register_url('games_new', create_new, handle_response=True)
        register_url('games_list', get_list)
        register_url('game_lobby', send_lobby_info)
        register_url('game_join', join_lobby, handle_response=True)
        register_url('game_leave', leave_lobby, handle_response=True)
