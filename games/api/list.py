from flask_socketio import emit

from auth.helpers import authenticated_only
from core.models import Lobby, Game
from utils.server import app
from utils.redis import redis


@authenticated_only
def get_list():
    app.logger.info(
        'Games list'
    )
    game_ids = redis.smembers(Lobby.key)
    games = []
    for game_id in games_ids:
        games.append(Game.get_by_id(redis, game_id, [Game.data]))
        
    emit('games', [game.serialize() for game in games])
