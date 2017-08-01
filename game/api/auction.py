from flask_socketio import emit

import config

from auth.helpers import authenticated_only
from base.decorators import game_response
from base.exceptions import EnergynetException
from core.constants import StepTypes
from core.models import Game, User, Player
from game.logic import get_auction_data, notify_game_players
from utils.redis import redis, redis_retry_transaction


@authenticated_only
def get_auction(user_id, data):
    user = User.get_by_id(redis, user_id, [User.current_game_id])

    game_id = user.current_game_id

    game_map = Game.map.read(redis, game_id)

    map_config = config.config.maps.get(game_map)

    emit('auction', get_auction_data(game_id, map_config))


@authenticated_only
@game_response('auction_bid')
def auction_bid(user_id, data):
    bid = data.get('bid')
    station = data.get('station')

    pipe = redis.pipeline()
    auction_bid_transaction(pipe, user_id, bid, station)

    return {'success': True}


@redis_retry_transaction()
def auction_bid_transaction(pipe, user_id, bid, station):
    user = User.get_by_id(redis, user_id, [User.current_game_id])
    game_id = user.current_game_id

    pipe.watch(Game.auction.key(game_id))

    game = Game.get_by_id(redis, game_id, [
        Game.map, Game.stations, Game.turn, Game.step, Game.auction,
        Game.order, Game.auction_user_ids, Game.auction_passed_user_ids,
        Game.user_ids, Game.phase,
    ])

    if game.turn != user_id:
        raise EnergynetException('Its not your move')
    if game.step != StepTypes.AUCTION:
        raise EnergynetException('Its not AUCTION')

    map_config = config.config.maps.get(game.map)
    active_count = map_config.get('activeStationsCount')
    if station not in game.stations[:active_count]:
        raise EnergynetException('Invalid station')

    if game.auction.get('bid') and game.auction.get('bid') >= bid:
        raise EnergynetException('Bid has to be bigger')
    if bid < station:
        raise EnergynetException('Bid has to be bigger')

    if game.get_users_left_for_auction() == {user_id}:
        winner = Player.get_by_id(redis, user_id, [Player.stations])

        _add_station_to_winner(pipe, winner, game, station, map_config)
        Game.auction_user_ids.delete(pipe, game.id)
    else:
        Game.auction.write(pipe, {
            'bid': bid,
            'station': station,
            'user_id': user_id,
        }, game_id)

        player = Player.get_by_id(redis, user_id, [])
        _game_next_turn_user(pipe, game, player)

    pipe.execute()

    notify_game_players(game.id)


@authenticated_only
@game_response('auction_pass')
def auction_pass(user_id, data):
    pipe = redis.pipeline()
    auction_pass_transaction(pipe, user_id)

    return {'success': True}


@redis_retry_transaction()
def auction_pass_transaction(pipe, user_id):
    user = User.get_by_id(redis, user_id, [User.current_game_id])
    game_id = user.current_game_id

    pipe.watch(Game.auction.key(game_id))
    pipe.watch(Game.auction_user_ids.key(game_id))
    pipe.watch(Game.step.key(game_id))
    pipe.watch(Game.turn.key(game_id))

    game = Game.get_by_id(redis, game_id, [
        Game.auction_user_ids, Game.step, Game.auction, Game.order, Game.map,
        Game.user_ids, Game.turn, Game.auction_passed_user_ids, Game.stations,
        Game.phase, Game.passed_count,
    ])

    player = Player.get_by_id(redis, user_id, [
        Player.stations,
    ])

    if game.turn != user_id:
        raise EnergynetException('Its not your move')

    if game.step != StepTypes.AUCTION:
        raise EnergynetException('Its not AUCTION')

    map_config = config.config.maps.get(game.map)

    if game.has_active_station_in_auction():
        users_left = game.get_users_left_for_auction() - {user_id}
        if len(users_left) == 1:
            winner_id = next(iter(users_left))
            winner = Player.get_by_id(redis, winner_id, [Player.stations])

            station = game.auction.get('station')
            _add_station_to_winner(pipe, winner, game, station, map_config)

            Game.auction_passed_user_ids.delete(pipe, game_id)
            Game.auction.delete(pipe, game_id)
        else:
            player = Player.get_by_id(redis, user_id, [])
            _game_next_turn_user(pipe, game, player)
            pipe.sadd(Game.auction_passed_user_ids.key(game.id), player.id)
    else:
        if game.phase == 0:
            raise EnergynetException('You cannot pass')
        else:
            _remove_stations_on_pass(pipe, game, map_config)

            if game.get_users_left_for_auction() == {player.id}:
                _move_to_next_stage(pipe, game)
                Game.auction_user_ids.delete(pipe, game.id)
            else:
                _game_next_turn_user(pipe, game, player)
                pipe.sadd(Game.auction_user_ids.key(game.id), player.id)

    pipe.execute()

    notify_game_players(game.id)


def _move_to_next_stage(pipe, game):
    Game.step.write(pipe, StepTypes.RESOURCES_BUY, game.id)
    Game.turn.write(pipe, game.order[-1], game.id)


def _remove_stations_on_pass(pipe, game, map_config):
    pipe.incr(Game.passed_count.key(game.id))

    auction_config = map_config.get('auction')
    visible_stations = game.get_sorted_stations(map_config)
    if auction_config.get('removeOnFirstPass') and game.passed_count == 0:
        pipe.lrem(Game.stations.key(game.id), 0, visible_stations[0])

    users_left = game.get_users_left_for_auction()
    if auction_config.get('removeOnAnyonePass') and len(users_left) == 1:
        pipe.lrem(Game.stations.key(game.id), 0, visible_stations[0])


def _add_station_to_winner(pipe, player, game, station, map_config):
    user_stations_count = map_config.get('userStationsCount')
    stations_limit = user_stations_count[len(game.user_ids) + 1]
    if len(player.stations) == stations_limit:
        Game.turn.write(pipe, player.id, game.id)
        Game.step.write(pipe, StepTypes.STATION_REMOVE, game.id)
    else:
        if game.phase == 0:
            # reorder
            data_by_users = game.get_order_data_by_users(redis)
            data_by_users[player.id] = (data_by_users[player.id][0], max(
                data_by_users[player.id][1], station
            ))
            new_order = [u_id for u_id, _ in sorted(
                data_by_users.items(), key=lambda d: d[1], reverse=True
            )]
            Game.order.delete(pipe, game.id)
            Game.order.write(pipe, new_order, game.id)
            Game.step.write(pipe, StepTypes.RESOURCES_BUY, game.id)
            Game.turn.write(pipe, new_order[-1], game.id)
        else:
            _game_station_bought_next_turn_user(pipe, game, player)
    pipe.lrem(Game.stations.key(game.id), 0, station)
    pipe.sadd(Player.stations.key(player.id), station)


def _game_station_bought_next_turn_user(pipe, game, player):
    next_user_id = game.get_next_user_id(
        player.id, exclude_ids=game.auction_user_ids.union({player.id})
    )
    if next_user_id:
        Game.turn.write(pipe, next_user_id, game.id)
    else:
        _move_to_next_stage(pipe, game)


def _game_next_turn_user(pipe, game, player):
    next_user_id = game.get_next_user_id(
        player.id, exclude_ids=game.auction_off_user_ids
    )
    Game.turn.write(pipe, next_user_id, game.id)
