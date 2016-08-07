from flask_socketio import emit

from games.models import Game


def get_list():
    games = Game.get_all()
    emit('games', games)
