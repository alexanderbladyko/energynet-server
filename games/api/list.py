from flask_socketio import emit

from auth.helpers import authenticated_only
from core.models import Lobby, Game
from utils.server import app


@authenticated_only
def get_list():
    app.logger.info(
        'Games list'
    )
    lobbies = Lobby.get_all([])
    games = Game.get_by_ids([l.id for l in lobbies], [Game.data])
    emit('games', [game.serialize() for game in games])
