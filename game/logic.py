from flask_socketio import emit

from core.models import Game, Player
from utils.redis import redis


def notify_game_players(game_id):
    game = Game.get_by_id(redis, game_id)

    users = []
    for user_id in game.user_ids:
        user = Player.get_by_id(redis, user_id)

        users.append(user.serialize())

    response = {
        'meta': game.serialize(),
        'data': users,
    }

    room_key = 'games:%s' % game.id
    emit('game', response, room=room_key)
