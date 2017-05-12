from flask_socketio import emit
from flask_login import current_user

from auth.helpers import authenticated_only
from core.logic import leave_game
from core.models import User, Game, Lobby
from games.logic import notify_lobby_users
from utils.redis import (
    redis_retry_transaction, redis, RedisTransactionException
)
from utils.server import app


@authenticated_only
def leave_lobby(data):
    app.logger.info('Leaving lobby')
    user = User.get_by_id(redis, current_user.id, [User.current_lobby_id])

    if not user.current_lobby_id:
        emit('leave_game', {
            'success': False,
            'message': 'User is not in the lobby'
        })
        return

    game_id = user.current_lobby_id

    if not redis.sismember(Lobby.key, game_id):
        emit('join_game', {
            'success': False,
            'message': 'No such game'
        })
        return

    pipe = redis.pipeline()
    try:
        remove_user_to_game(pipe, game_id, user.id)
    except RedisTransactionException:
        emit('join_game', {
            'success': False,
            'message': 'Failed to add user to game'
        })
        return
    except:
        emit('join_game', {
            'success': False,
            'message': 'Unknown exception'
        })
        return

    leave_game(game_id)

    emit('leave_game', {
        'success': True,
    })
    notify_lobby_users(game_id=game_id)


@redis_retry_transaction()
def remove_user_to_game(pipe, game_id, user_id):
    pipe.watch(Game.user_ids.key(game_id))
    pipe.watch(User.current_lobby_id.key(user_id))

    pipe.delete(User.current_lobby_id.key(user_id))
    pipe.srem(Game.user_ids.key(game_id), user_id)
