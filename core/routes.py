
from utils.server import blueprint, socketio, register_url
from core.api.socket import ws_connect, error_handler, default_error_handler
from core.api.geo import geo_data
from core.api.map_data import map_data
from core.api.state import get_state


class CoreRoutes(object):
    def init_routes(self):
        blueprint.route('/game_api/map/<string:map_name>/geo')(geo_data)
        blueprint.route('/game_api/map/<string:map_name>/map_data')(map_data)

        socketio.on('connect')(ws_connect)
        socketio.on_error()(error_handler)
        socketio.on_error_default(default_error_handler)
        register_url('state', get_state)
