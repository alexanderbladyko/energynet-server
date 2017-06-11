from utils.blueprint import blueprint
from utils.config import config

from auth.api.user_info import get_user_info
from auth.api.fake_login import fake_login
from auth.api.login import login
from auth.api.logout import logout
from auth.api.register import register


class AuthRoutes(object):
    def init_routes(self):
        auth_api = config.get('urls', 'auth_api')

        if config.get('app', 'debug'):
            blueprint.route('{0}/fake/login/<int:user_id>'.format(auth_api), methods=['GET'])(fake_login)  # noqa
        blueprint.route('{0}/login'.format(auth_api), methods=['POST'])(login)
        blueprint.route('{0}/register'.format(auth_api), methods=['POST'])(register)  # noqa
        blueprint.route('{0}/logout'.format(auth_api), methods=['GET', 'POST'])(logout)  # noqa
        blueprint.route('{0}/user_info'.format(auth_api), methods=['GET', 'POST'])(get_user_info)  # noqa
