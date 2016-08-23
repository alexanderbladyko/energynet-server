from utils.socket_server import io

from lobby.api.join import join_lobby
from lobby.api.lobby import get_lobby
from lobby.api.leave import leave_lobby


class LobbyRoutes(object):
    def init_routes(self):
        io.on('lobby')(get_lobby)
        io.on('join')(join_lobby)
        io.on('leave')(leave_lobby)
