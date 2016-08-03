from flask_login import LoginManager

from auth.models import User
from utils.server import app


login_manager = LoginManager()

login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)
