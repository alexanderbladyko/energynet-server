from flask_socketio import emit
from flask_login import current_user

from auth.helpers import authenticated_only
from core.models import User, Game, Lobby
from core.logic import join_room
from games.logic import get_lobbies
from utils.redis import (
    redis, redis_retry_transaction, RedisTransactionException
)
from utils.server import app


@authenticated_only
def create_new(data):
    name = data['name']
    players_limit = data['playersLimit']

    app.logger.info(
        'New game creating (%s, %s)' % (name, players_limit)
    )

    user = User.get_by_id(redis, current_user.id)
    if user.current_lobby_id or user.current_game_id:
        emit('new', {
            'success': False,
            'message': 'User is already in the game'
        })
        return

    pipe = redis.pipeline()
    try:
        game_id = create_new_game(pipe, name, players_limit, user.id)
    except RedisTransactionException:
        emit('new_game', {
            'success': False,
            'message': 'Failed to add user to game'
        })
        return
    except:
        emit('new_game', {
            'success': False,
            'message': 'Unknown exception'
        })
        return

    join_room(game_id)

    emit('new_game', {
        'success': True,
    })
    emit('games', get_lobbies(), namespace='/games', broadcast=True)


@redis_retry_transaction()
def create_new_game(pipe, name, players_limit, user_id):
    pipe.watch([
        Game.index(), User.current_lobby_id.key(user_id), Game.key, Lobby.key,
    ])

    game_id = pipe.incr(Game.index())
    Game.data.write(pipe, {
        'name': name,
        'players_limit': players_limit,
    }, game_id)
    Game.owner_id.write(pipe, user_id, game_id)
    Game.user_ids.write(pipe, [user_id], game_id)

    pipe.sadd(Lobby.key, game_id)

    User.current_lobby_id.write(pipe, game_id, user_id)

    pipe.execute()
    return game_id
