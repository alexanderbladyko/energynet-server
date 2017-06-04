from flask_socketio import emit
from flask_login import current_user

import config

from auth.helpers import authenticated_only
from base.decorators import game_response
from base.exceptions import EnergynetException
from core.constants import StepTypes
from core.models import User, Game, Lobby, Player
from game.logic import notify_game_players
from utils.redis import redis_retry_transaction, redis
from utils.server import app


@authenticated_only
@game_response(topic='start_game')
def start_game(data):
    app.logger.info('Starting game')

    user = User.get_by_id(redis, current_user.id, [User.current_lobby_id])

    game_id = user.current_lobby_id

    pipe = redis.pipeline()
    start_game_transaction(pipe, game_id, user.id)

    emit('start', {
        'success': True,
    })

    notify_game_players(game_id)


@redis_retry_transaction()
def start_game_transaction(pipe, game_id, user_id):
    pipe.watch(Lobby.key)
    pipe.watch(User.current_lobby_id.key(user_id))

    if not game_id:
        pipe.unwatch()
        raise EnergynetException(message='User is not in the game')

    game = Game.get_by_id(pipe, game_id, [
        Game.owner_id, Game.user_ids, Game.map,
    ])

    if game.owner_id != user_id:
        pipe.unwatch()
        raise EnergynetException(message='User is not the owner of the game')

    players_limit = int(pipe.hget(Game.data.key(game_id), 'players_limit'))
    if len(game.user_ids) != players_limit:
        pipe.unwatch()
        raise EnergynetException(message='Not enough players to start game')

    pipe.srem(Lobby.key, game_id)

    pipe.set(Game.step.key(game_id), StepTypes.COLORS)

    for player_id in game.user_ids:
        pipe.delete(User.current_lobby_id.key(player_id))
        Player.cash.write(
            pipe, config.config.maps.get(game.map).get('startCash'), player_id
        )

    pipe.execute()
