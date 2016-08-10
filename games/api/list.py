from flask_socketio import emit

from games.models import Game
from auth.helpers import authenticated_only


@authenticated_only
def get_list():
    games = Game.get_all()
    emit('games', games)
