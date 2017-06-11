from utils.server import socketio
from games.api.find import find_game
from games.api.list import get_list
from games.api.new import create_new
from games.api.join import join_lobby
from games.api.lobby import send_lobby_info
from games.api.leave import leave_lobby


class GamesRoutes(object):
    def init_routes(self):
        socketio.on_event('find_game', find_game)
        socketio.on_event('new_game', create_new)
        socketio.on_event('list', get_list)
        socketio.on_event('lobby', send_lobby_info)
        socketio.on_event('join_game', join_lobby)
        socketio.on_event('leave_game', leave_lobby)
