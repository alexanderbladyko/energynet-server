from utils.server import blueprint, socketio

from core.api.config import get_config
from core.api.socket import (
    ws_connect, ws_disconnect, error_handler, default_error_handler
)
from core.api.state import get_state


class CoreRoutes(object):
    def init_routes(self):
        blueprint.route('/config')(get_config)

        socketio.on('connect')(ws_connect)
        # socketio.on('disconnect')(ws_disconnect)
        # socketio.on_error()(error_handler)
        # socketio.on_error_default(default_error_handler)
        socketio.on_event('state', get_state)
