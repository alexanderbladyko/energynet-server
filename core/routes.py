from utils.server import app
from utils.socket_server import io

from core.api.config import get_config
from core.api.socket import (
    ws_connect, ws_disconnect, error_handler, default_error_handler
)
from core.api.state import get_state


class CoreRoutes(object):
    def init_routes(self):
        app.route('/config')(get_config)

        io.on('connect')(ws_connect)
        io.on('disconnect')(ws_disconnect)
        # io.on_error()(error_handler)
        # io.on_error_default(default_error_handler)
        io.on('state')(get_state)
