from utils.socket_server import io

from lobby.api.join import join_lobby


class LobbyRoutes(object):
    def init_routes(self):
        io.on('join')(join_lobby)
