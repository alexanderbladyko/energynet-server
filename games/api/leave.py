from flask_socketio import emit

from auth.helpers import authenticated_only
from base.exceptions import EnergynetException
from base.decorators import game_response
from core.logic import leave_game
from core.models import User, Game, Lobby
from games.logic import notify_lobby_users
from utils.redis import redis_retry_transaction, redis


@authenticated_only
@game_response(topic='leave_game')
def leave_lobby(user_id, data):
    # app.logger.info('Leaving lobby')
    user = User.get_by_id(redis, user_id, [User.current_lobby_id])

    if not user.current_lobby_id:
        raise EnergynetException(message='User is not in the lobby')

    game_id = user.current_lobby_id

    pipe = redis.pipeline()
    remove_user_to_game(pipe, game_id, user.id)

    leave_game(game_id)

    emit('leave_game', {
        'success': True,
    })
    notify_lobby_users(game_id=game_id)


@redis_retry_transaction()
def remove_user_to_game(pipe, game_id, user_id):
    pipe.watch(Game.user_ids.key(game_id))
    pipe.watch(User.current_lobby_id.key(user_id))

    if not pipe.sismember(Lobby.key, game_id):
        pipe.unwatch()
        raise EnergynetException(message='No such game')

    pipe.delete(User.current_lobby_id.key(user_id))
    pipe.srem(Game.user_ids.key(game_id), user_id)
