from utils.server import app

from core.api.config import config


class CoreRoutes(object):
    def init_routes(self):
        app.route('/config')(config)
