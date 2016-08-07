from utils.socket_server import io
from games.api.list import get_list
from games.api.new import create_new


class GamesRoutes(object):
    def init_routes(self):
        io.on('connect', namespace='/games')(get_list)
        io.on('new', namespace='/games')(create_new)
