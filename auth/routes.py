from utils.server import app
from utils.config import config

from auth.api.login import login
from auth.api.fake_login import fake_login
from auth.api.register import register
from auth.api.logout import logout


class AuthRoutes(object):
    def init_routes(self):
        auth_api = config.get('urls', 'auth_api')

        if config.get('app', 'debug'):
            app.route('{0}/fake/login/<int:user_id>'.format(auth_api), methods=['GET'])(fake_login)  # noqa
        app.route('{0}/login'.format(auth_api), methods=['POST'])(login)
        app.route('{0}/register'.format(auth_api), methods=['POST'])(register)
        app.route('{0}/logout'.format(auth_api), methods=['GET', 'POST'])(logout)  # noqa
