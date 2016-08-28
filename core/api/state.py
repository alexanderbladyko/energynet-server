from flask_socketio import emit
from flask_login import current_user

from games.models import User


def get_state(data):
    user = User.get_by_id(current_user.id)

    emit('state', {
        'inGame': bool(user.current_game_id),
        'inLobby': bool(user.current_lobby_id),
    })
