from flask_socketio import emit

from core.models import Game, Player
from utils.redis import redis


def notify_game_players(game_id):
    response = get_game_data(game_id)

    room_key = 'games:%s' % game_id
    emit('game', response, room=room_key)


def get_game_data(game_id):
    game = Game.get_by_id(redis, game_id)

    users = []
    for user_id in game.user_ids:
        user = Player.get_by_id(redis, user_id)

        users.append(user.serialize())

    return {
        'meta': game.serialize(),
        'data': users,
    }
