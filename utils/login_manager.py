from flask_login import LoginManager

from auth.models import User
from utils.server import app


def init_login_manager():
    login_manager = LoginManager()
    login_manager.init_app(app)

    login_manager.user_loader(load_user)


def load_user(user_id):
    return User.get_by_id(user_id)
