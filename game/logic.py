import random
from flask_socketio import emit

from core.models import Game, Player, User
from utils.redis import redis


def notify_game_players(game_id):
    response = get_game_data(game_id)

    room_key = 'games:%s' % game_id
    emit('game', response, room=room_key)


def get_game_data(game_id):
    game = Game.get_by_id(redis, game_id)

    users = []
    for user_id in game.user_ids:
        player = Player.get_by_id(redis, user_id)
        user = User.get_by_id(redis, user_id, [User.data])
        user_data = player.serialize()
        user_data.update(user.serialize([User.data]))

        users.append(user_data)

    return {
        'meta': game.serialize([
            Game.user_ids,
            Game.data,
            Game.stations,
            Game.owner_id,
            Game.turn,
            Game.phase,
            Game.step,
            Game.areas,
            Game.auction,
            Game.map,
            Game.resources,
        ]),
        'data': users,
    }


def get_start_stations(map_config):
    stations = map_config.get('stations')
    initial_rules = map_config.get('initialStationRules')

    exclude_list = [station.get('cost') for station in initial_rules]
    result_list = [
        station.get('cost') for station in stations
        if station.get('cost') not in exclude_list
    ]
    random.shuffle(result_list)
    for rule in initial_rules:
        new_index = rule.get('place')
        if 'delta' in rule:
            new_index += random.randint(0, rule.get('delta'))
        if new_index == -1:
            result_list.append(rule.get('cost'))
        else:
            result_list.insert(new_index, rule.get('cost'))
    return result_list


def get_auction_data(game_id, map_config):
    active_count = map_config.get('activeStationsCount')
    visible_count = map_config.get('visibleStationsCount')

    stations = Game.stations.read(redis, game_id)
    data = []
    for index in range(visible_count):
        data.append({
            'cost': stations[index],
            'available': index < active_count,
        })
    return {
        'meta': {
            'left': len(stations),
        },
        'data': data
    }
