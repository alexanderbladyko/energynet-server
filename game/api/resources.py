from flask_socketio import emit

import config

from auth.helpers import authenticated_only
from base.decorators import game_response
from base.exceptions import EnergynetException
from core.constants import StepTypes
from core.models import Game, User, Player
from game.logic import notify_game_players
from utils.redis import redis, redis_retry_transaction


@authenticated_only
def get_resources(user_id, data):
    user = User.get_by_id(redis, user_id, [User.current_game_id])

    game_id = user.current_game_id

    emit('resources', Game.resources.read(redis, game_id))


@authenticated_only
@game_response('resource_buy')
def resource_buy(user_id, data):
    pipe = redis.pipeline()
    resource_buy_transaction(pipe, user_id, data)

    return {'success': True}


@redis_retry_transaction()
def resource_buy_transaction(pipe, user_id, resources):
    user = User.get_by_id(redis, user_id, [User.current_game_id])
    game_id = user.current_game_id

    pipe.watch(*[
        Game.auction.key(game_id),
        Game.auction_user_ids.key(game_id),
        Game.step.key(game_id),
        Game.turn.key(game_id),
        Game.resources.key(game_id),
        Player.resources.key(user_id),
    ])

    game = Game.get_by_id(redis, game_id, [
        Game.map, Game.turn, Game.step, Game.user_ids, Game.order,
        Game.resources,
    ])

    if game.turn != user_id:
        raise EnergynetException('Its not your move')
    if game.step != StepTypes.STATION_REMOVE:
        raise EnergynetException('Its not STATION_REMOVE')

    map_config = config.config.maps.get(game.map)

    player = Player.get_by_id(redis, user_id, [
        Player.stations, Player.resources, Player.cash
    ])
    can_hold, reason = player.can_hold_new_resources(map_config, resources)
    if not can_hold:
        raise EnergynetException(reason)

    can_purchase, price = game.get_resource_price(map_config, resources)
    if not can_purchase:
        raise EnergynetException('Not enough resources')

    if player.cash < price:
        raise EnergynetException('Not enough cash')

    next_step = False
    index = game.order.index(user_id)
    if index <= 0:
        next_step = True

    if next_step:
        next_user_id = game.order[-1]
    else:
        next_user_id = game.order[index - 1]

    Game.turn.write(pipe, next_user_id, game.id)
    if next_step:
        Game.step.write(pipe, StepTypes.CITIES_BUY, game.id)

    game_resources_left = dict(
        (resource, count - resources.get(resource))
        for resource, count in game.resources.items()
    )
    Game.resources.write(pipe, game_resources_left, game.id)

    player_resources_now = dict(
        (resource, (count or 0) + resources.get(resource))
        for resource, count in player.resources.items()
    )
    Player.resources.write(pipe, player_resources_now, player.id)

    pipe.execute()

    notify_game_players(game.id)
