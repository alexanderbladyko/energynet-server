from flask_socketio import emit
from flask_login import current_user

from auth.helpers import authenticated_only
from base.decorators import game_response
from base.exceptions import EnergynetException
from core.models import User, Game, Lobby
from utils.redis import redis_retry_transaction, redis
from utils.server import app


@authenticated_only
@game_response(topic='start_game')
def start_game(data):
    app.logger.info('Starting game')
    user = User.get_by_id(redis, current_user.id, [User.current_lobby_id])

    game_id = user.current_lobby_id

    if not game_id:
        raise EnergynetException(message='User is not in the game')

    pipe = redis.pipeline()
    start_game_transaction(pipe, game_id, user.id)

    emit('start', {
        'success': True,
    })


@redis_retry_transaction()
def start_game_transaction(pipe, game_id, user_id):
    pipe.watch(Lobby.key)

    if user_id != Game.owner_id.read(redis, game_id):
        pipe.unwatch()
        raise EnergynetException(message='User is not the owner of the game')

    pipe.srem(Lobby.key, game_id)
    pass
