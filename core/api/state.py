from flask_socketio import emit

from auth.helpers import authenticated_only
from core.models import User
from utils.redis import redis


@authenticated_only
def get_state(user_id, data):
    user = User.get_by_id(redis, user_id, [
        User.current_game_id,
        User.current_lobby_id,
    ])

    emit('state', {
        'inGame': bool(user.current_game_id),
        'inLobby': bool(user.current_lobby_id),
    })
