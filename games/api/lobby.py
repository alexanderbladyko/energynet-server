from flask_socketio import join_room
from flask_login import current_user

from core.models import User
from games.logic import notify_lobby_users


def send_lobby_info(data):

    user = User.get_by_id(current_user.id, [User.current_lobby_id])
    if not user.current_lobby_id:
        return

    room_key = 'games:%s' % id
    join_room(room_key)

    notify_lobby_users(user.current_lobby_id)
