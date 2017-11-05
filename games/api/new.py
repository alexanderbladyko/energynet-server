from flask_socketio import emit

from auth.helpers import authenticated_only
from base.exceptions import EnergynetException
from core.models import User, Game, Lobby
from core.logic import join_game
from games.logic import notify_user_finding_game, unsubscribe_from_games
from utils.config import config
from utils.redis import (
    redis, redis_retry_transaction, RedisTransactionException
)


@authenticated_only
def create_new(user_id, data):
    name = data['name']
    players_limit = data['playersLimit']
    game_map = data['map']
    areas = data['areas']
    game_id = None
    if config.get('app', 'debug'):
        game_id = data.get('id')

    # app.logger.info('New game creating (%s, %s)' % (name, players_limit))

    user = User.get_by_id(redis, user_id)
    if user.current_lobby_id or user.current_game_id:
        raise EnergynetException(message='User is already in the game')

    pipe = redis.pipeline()
    try:
        game_id = create_new_game(
            pipe, name, players_limit, user.id, game_map, areas,
            game_id=game_id,
        )
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
def create_new_game(
    pipe, name, players_limit, user_id, game_map, areas, game_id=None
):
    pipe.watch([
        Game.index(), User.current_lobby_id.key(user_id), Game.key, Lobby.key,
    ])

    game_id = game_id or pipe.incr(Game.index())
    Game.data.write(pipe, {
        'name': name,
        'players_limit': players_limit,
    }, game_id)
    Game.owner_id.write(pipe, user_id, game_id)
    Game.user_ids.write(pipe, [user_id], game_id)
    Game.map.write(pipe, game_map, game_id)
    Game.phase.write(pipe, 0, game_id)
    Game.areas.write(pipe, areas, game_id)

    pipe.sadd(Lobby.key, game_id)

    User.current_game_id.write(pipe, game_id, user_id)
    User.current_lobby_id.write(pipe, game_id, user_id)

    pipe.execute()
    return game_id
