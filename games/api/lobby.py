from auth.helpers import authenticated_only
from core.logic import join_game
from core.models import User
from games.logic import notify_lobby_users
from utils.redis import redis


@authenticated_only
def send_lobby_info(user_id, data):

    user = User.get_by_id(redis, user_id, [User.current_lobby_id])
    if not user.current_lobby_id:
        return

    join_game(user.current_lobby_id)

    notify_lobby_users(user.current_lobby_id)
