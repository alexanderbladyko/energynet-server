import config

from auth.helpers import authenticated_only
from base.exceptions import EnergynetException
from core.constants import StepTypes
from core.models import Game, User, Player
from game.logic import notify_game_players
from utils.redis import redis, redis_retry_transaction


@authenticated_only
def finance_receive(user_id, data):
    stations = data.get('stations')

    pipe = redis.pipeline()
    finance_receive_transaction(pipe, user_id, stations)

    return {'success': True}


@redis_retry_transaction()
def finance_receive_transaction(pipe, user_id, stations):
    user = User.get_by_id(redis, user_id, [User.current_game_id])
    game_id = user.current_game_id

    pipe.watch(Game.step.key(game_id))
    pipe.watch(Game.turn.key(game_id))
    pipe.watch(Player.cities.key(user_id))
    pipe.watch(Player.cash.key(user_id))

    player = Player.get_by_id(redis, user_id, [
        Player.cities, Player.stations, Player.cash, Player.resources
    ])

    used_stations = [float(s) for s in stations.keys()]
    if set(used_stations) - player.stations != set():
        raise EnergynetException('Stations are not matching')

    game = Game.get_by_id(redis, game_id, [
        Game.map, Game.turn, Game.step, Game.user_ids, Game.order,
        Game.areas, Game.resources,
    ])

    if game.turn != user_id:
        raise EnergynetException('Its not your move')
    if game.step != StepTypes.FINANCE_RECEIVE:
        raise EnergynetException('Its not FINANCE_RECEIVE')

    map_config = config.config.maps.get(game.map)
    user_stations = player.get_user_stations(map_config)

    efficiency = 0
    for user_station in user_stations:
        station = user_station['cost']
        if station not in used_stations:
            continue
        resources = user_station['resources']
        station_efficiency = user_station['efficiency']
        capacity = user_station['capacity']
        req_resources = stations[str(float(station))]
        req_res = set(r for r in req_resources.keys() if req_resources[r] > 0)
        if req_res - set(resources) != set():
            raise EnergynetException(
                'Wrong resources for station {}'.format(station)
            )

        resources_count = sum(req_resources.values())
        if resources_count < capacity:
            raise EnergynetException(
                'Not enough resources for station {}'.format(station)
            )
        efficiency += station_efficiency

    heated_cities = min(efficiency, len(player.cities.keys()))
    payment_config = map_config.get('payment')

    payment = (
        payment_config[heated_cities]
        if heated_cities < len(payment_config)
        else payment_config[-1]
    )
    Player.cash.write(pipe, player.cash + payment, user_id)

    next_resources = player.resources.copy()
    for resources in stations.values():
        for resource in resources.keys():
            next_resources[resource] -= resources[resource]
    if min(next_resources.values()) < 0:
        raise EnergynetException('Not enough resources')
    Player.resources.write(pipe, next_resources, user_id)

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
        # TODO: check winner
        Game.step.write(pipe, StepTypes.AUCTION, game.id)

    pipe.execute()

    notify_game_players(game.id)
