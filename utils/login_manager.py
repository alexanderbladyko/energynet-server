from flask_login import LoginManager

from auth.models import User


def load_user(user_id):
    return User.get_by_id(user_id)

login_manager = LoginManager()
login_manager.user_loader(load_user)
