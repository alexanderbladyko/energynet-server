from flask_socketio import emit

from games.models import GamesList
from auth.helpers import authenticated_only


@authenticated_only
def get_list():
    games_list = GamesList()
    games = games_list.get_all()
    emit('games', [game.data for game in games])
