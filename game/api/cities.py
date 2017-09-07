import config

from auth.helpers import authenticated_only
from base.decorators import game_response
from base.exceptions import EnergynetException
from core.constants import StepTypes
from core.models import Game, User, Player
from game.graph import get_closest_paths
from game.logic import notify_game_players
from utils.redis import redis, redis_retry_transaction


@authenticated_only
@game_response('cities_buy')
def cities_buy(user_id, data):
    cities = data.get('cities')

    pipe = redis.pipeline()
    cities_buy_transaction(pipe, user_id, cities)

    return {'success': True}


@redis_retry_transaction()
def cities_buy_transaction(pipe, user_id, cities):
    user = User.get_by_id(redis, user_id, [User.current_game_id])
    game_id = user.current_game_id

    pipe.watch(Game.step.key(game_id))
    pipe.watch(Game.turn.key(game_id))
    pipe.watch(Player.cities.key(user_id))
    pipe.watch(Player.cash.key(user_id))

    player = Player.get_by_id(redis, user_id, [Player.cities, Player.cash])

    if set(player.cities.key()).intersection(set(cities)):
        raise EnergynetException('Cities already owned by user')

    game = Game.get_by_id(redis, game_id, [
        Game.map, Game.turn, Game.step, Game.user_ids, Game.order, Game.areas,
    ])

    if game.turn != user_id:
        raise EnergynetException('Its not your move')
    if game.step != StepTypes.CITIES_BUY:
        raise EnergynetException('Its not STATION_REMOVE')

    map_config = config.config.maps.get(game.map)
    city_by_name = {
        city['name']: city for city in map_config['cities']
        if city['name'] in cities
    }
    if [city for city in city_by_name.values()
            if city['area'] not in game.areas]:
        raise EnergynetException('There is city outside of area')

    taken_cities = {}
    for p_id in game.user_ids:
        for city, slot in Player.cities.read(redis, p_id).items():
            if city not in taken_cities:
                taken_cities[city] = []
            taken_cities[city].append(slot)

    request_cities = {}
    for city_name, city in city_by_name.items():
        free_slots = set(city['slots']) - set(taken_cities.get(city_name, []))
        if free_slots:
            request_cities[city_name] = min(free_slots)
        else:
            raise EnergynetException('No slots for {}'.format(city_name))

    paths = get_closest_paths(map_config, player.cities.keys(), cities)

    price = sum(paths.values() + request_cities.values())
    if player.cash < price:
        raise EnergynetException('Not enough cash to buy cities')

    Player.write(pipe, player.cash - price, user_id)
    pipe.hmset(Player.cities.key(id), request_cities)

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
        Game.step.write(pipe, StepTypes.FINANCE_RECEIVE, game.id)

    pipe.execute()

    notify_game_players(game.id)
