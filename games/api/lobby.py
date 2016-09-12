from flask_login import current_user

from core.logic import join_game
from core.models import User
from games.logic import notify_lobby_users


def send_lobby_info(data):

    user = User.get_by_id(current_user.id, [User.current_lobby_id])
    if not user.current_lobby_id:
        return

    join_game(user.current_lobby_id)

    notify_lobby_users(user.current_lobby_id)
