from flask_socketio import emit
from flask_login import current_user

from auth.helpers import authenticated_only
from core.logic import join_game
from core.models import User, Game, Lobby
from games.logic import notify_lobby_users
from utils.redis import (
    redis_retry_transaction, redis, RedisTransactionException
)
from utils.server import app


@authenticated_only
def join_lobby(data):
    app.logger.info(
        'Join lobby'
    )
    game_id = data['id']

    user = User.get_by_id(redis, current_user.id)

    if user.current_lobby_id or user.current_game_id:
        emit('join_game', {
            'success': False,
            'message': 'User is already in the game'
        })
        return

    if not redis.sismember(Lobby.key, game_id):
        emit('join_game', {
            'success': False,
            'message': 'No such game'
        })
        return

    pipe = redis.pipeline()
    try:
        add_user_to_game(pipe, game_id, user.id)
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

    join_game(game_id)

    emit('join_game', {
        'success': True,
    })
    notify_lobby_users(game_id=game_id)


@redis_retry_transaction()
def add_user_to_game(pipe, game_id, user_id):
    pipe.watch(Game.user_ids.key(game_id))
    pipe.watch(User.current_lobby_id.key(user_id))

    pipe.set(User.current_lobby_id.key(user_id), game_id)
    pipe.sadd(Game.user_ids.key(game_id), user_id)
