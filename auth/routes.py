from utils.blueprint import blueprint
from utils.config import config

from auth.api.user_info import get_user_info
from auth.api.fake_login import fake_login
from auth.api.login import login
from auth.api.logout import logout
from auth.api.register import register


class AuthRoutes(object):
    def init_routes(self):

        if config.get('app', 'debug'):
            blueprint.route('/auth/fake/login/<int:user_id>', methods=['GET'])(fake_login)  # noqa
        blueprint.route('/auth/login', methods=['POST'])(login)
        blueprint.route('/auth/register', methods=['POST'])(register)
        blueprint.route('/auth/logout', methods=['GET', 'POST'])(logout)
        blueprint.route('/auth/user_info', methods=['GET', 'POST'])(get_user_info)  # noqa
