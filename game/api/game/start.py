from flask_socketio import emit
import random

import config

from auth.helpers import authenticated_only
from base.exceptions import EnergynetException
from core.constants import StepTypes
from core.logic import game_room_key
from core.models import User, Game, Lobby, Player
from game.logic import notify_game_players, get_start_stations
from utils.redis import redis_retry_transaction, redis


@authenticated_only
def start_game(user_id, data):
    user = User.get_by_id(redis, user_id, [User.current_lobby_id])

    game_id = user.current_lobby_id

    pipe = redis.pipeline()
    start_game_transaction(pipe, game_id, user.id)

    notify_game_players(game_id)

    emit('game_start', {'success': True}, room=game_room_key(game_id))


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

    map_config = config.config.maps.get(game.map)
    Game.resources.write(pipe, map_config.get('resourceInitials'), game_id)
    stations = get_start_stations(map_config)
    Game.stations.write(pipe, stations, game_id)

    users_order = list(game.user_ids)

    random.shuffle(users_order)
    Game.order.write(pipe, users_order, game_id)

    Game.turn.write(pipe, users_order[0], game_id)

    for player_id in game.user_ids:
        User.current_lobby_id.delete(pipe, player_id)
        Player.cash.write(
            pipe, map_config.get('startCash'), player_id
        )

    pipe.execute()
