from utils.socket_server import io
from games.api.list import get_list
from games.api.new import create_new
from games.api.join import join_lobby
from games.api.lobby import send_lobby_info
from games.api.leave import leave_lobby


class GamesRoutes(object):
    def init_routes(self):
        io.on('connect', namespace='/games')(get_list)
        io.on('new', namespace='/games')(create_new)
        io.on('get_lobby')(send_lobby_info)
        io.on('join')(join_lobby)
        io.on('leave')(leave_lobby)
