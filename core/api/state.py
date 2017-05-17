from flask_socketio import emit
from flask_login import current_user

from core.models import User
from utils.redis import redis


def get_state(data):
    user = User.get_by_id(redis, current_user.id, [
        User.current_game_id,
        User.current_lobby_id,
    ])

    emit('state', {
        'inGame': bool(user.current_game_id),
        'inLobby': bool(user.current_lobby_id),
    })
