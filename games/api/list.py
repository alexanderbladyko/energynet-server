from flask_socketio import emit

from auth.helpers import authenticated_only
from games.logic import get_lobbies


@authenticated_only
def get_list(message, user_id):
    emit('games_list', get_lobbies())
