from flask_socketio import emit

from auth.helpers import authenticated_only
from base.exceptions import EnergynetException
from core.logic import join_game
from core.models import User, Game, Lobby
from games.logic import notify_lobby_users, unsubscribe_from_games
from utils.redis import redis_retry_transaction, redis


@authenticated_only
def join_lobby(user_id, data):
    game_id = data['id']

    user = User.get_by_id(redis, user_id)

    if user.current_lobby_id or user.current_game_id:
        raise EnergynetException(message='User is already in the game')

    pipe = redis.pipeline()
    add_user_to_game(pipe, game_id, user.id)

    unsubscribe_from_games()
    join_game(game_id)

    emit('game_join', {
        'success': True,
    })
    notify_lobby_users(game_id=game_id)


@redis_retry_transaction()
def add_user_to_game(pipe, game_id, user_id):
    pipe.watch(Game.user_ids.key(game_id))
    pipe.watch(User.current_lobby_id.key(user_id))

    if not pipe.sismember(Lobby.key, game_id):
        pipe.unwatch()
        raise EnergynetException(message='No such game')

    players_limit = int(pipe.hget(Game.data.key(game_id), 'players_limit'))
    if pipe.scard(Game.user_ids.key(game_id)) == players_limit:
        pipe.unwatch()
        raise EnergynetException(message='Players limit of game exceeded')

    pipe.set(User.current_game_id.key(user_id), game_id)
    pipe.set(User.current_lobby_id.key(user_id), game_id)
    pipe.sadd(Game.user_ids.key(game_id), user_id)

    pipe.execute()
