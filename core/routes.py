from utils.server import blueprint, socketio

from core.api.config import get_config
from core.api.socket import (
    ws_connect
)
from core.api.geo import geo_data
from core.api.map_data import map_data
from core.api.state import get_state


class CoreRoutes(object):
    def init_routes(self):
        blueprint.route('/config')(get_config)
        blueprint.route('/game_api/map/<string:map_name>/geo')(geo_data)
        blueprint.route('/game_api/map/<string:map_name>/map_data')(map_data)

        socketio.on('connect')(ws_connect)
        socketio.on_event('state', get_state)
