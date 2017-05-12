from flask_socketio import emit

from core.models import Game, User
from utils.redis import redis


def notify_lobby_users(game_id):
    game = Game.get_by_id(redis, game_id, [
        Game.user_ids,
        Game.data,
    ])

    lobby_info = game.data.copy()
    users = list()
    for user_id in game.user_ids:
        user = User.get_by_id(redis, user_id, [User.data, User.game_data])

        users.append(user.serialize([User.data, User.game_data]))

    lobby_info.update({
        'users': users,
    })

    room_key = 'games:%s' % game.id
    emit('lobby', lobby_info, room=room_key)
