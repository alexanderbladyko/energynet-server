from flask_socketio import emit

from auth.helpers import authenticated_only
from base.decorators import game_response
from base.exceptions import EnergynetException
from core.models import User, Game, Lobby
from core.logic import join_game
from games.logic import notify_user_finding_game, unsubscribe_from_games
from utils.redis import (
    redis, redis_retry_transaction, RedisTransactionException
)


@authenticated_only
@game_response(topic='games_new')
def create_new(user_id, data):
    name = data['name']
    players_limit = data['playersLimit']

    # app.logger.info('New game creating (%s, %s)' % (name, players_limit))

    user = User.get_by_id(redis, user_id)
    if user.current_lobby_id or user.current_game_id:
        raise EnergynetException(message='User is already in the game')

    pipe = redis.pipeline()
    try:
        game_id = create_new_game(pipe, name, players_limit, user.id)
    except RedisTransactionException:
        raise EnergynetException(message='Failed to add user to game')
    except:
        raise EnergynetException(message='Unknown exception')

    unsubscribe_from_games()
    join_game(game_id)

    emit('games_new', {
        'success': True,
    })
    notify_user_finding_game()


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
