from flask_socketio import emit

from auth.helpers import authenticated_only
from games.logic import get_lobbies, subscribe_to_games


@authenticated_only
def find_game(user_id, message):
    subscribe_to_games()
    emit('games', get_lobbies())
