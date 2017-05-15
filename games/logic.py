from flask_socketio import emit

from core.models import Game, User, Lobby
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


def get_lobbies():
    game_ids = redis.smembers(Lobby.key)
    games = []
    for game_id in sorted(game_ids):
        game = Game.get_by_id(redis, int(game_id), [Game.data, Game.owner_id])
        games.append({
            'id': game.id,
            'name': game.data['name'],
            'playersLimit': game.data['players_limit'],
        })
    return games
