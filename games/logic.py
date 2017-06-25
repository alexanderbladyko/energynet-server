from flask_socketio import emit, join_room, leave_room

from core.models import Game, User, Lobby
from games.constants import FIND_GAME_ROOM_KEY
from utils.redis import redis


def notify_lobby_users(game_id):
    game = Game.get_by_id(redis, game_id, [
        Game.user_ids,
        Game.data,
        Game.owner_id,
    ])

    lobby_info = game.data.copy()
    users = list()
    for user_id in game.user_ids:
        user = User.get_by_id(redis, user_id, [User.data])

        users.append({
            'id': user.id,
            'name': user.data['name'],
        })

    lobby_info.update({
        'players': users,
        'users': [],
        'ownerId': game.owner_id
    })

    room_key = 'games:%s' % game.id
    emit('game_lobby', lobby_info, room=room_key)


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


def notify_user_finding_game():
    emit('games', get_lobbies(), room=FIND_GAME_ROOM_KEY)


def subscribe_to_games():
    join_room(FIND_GAME_ROOM_KEY)


def unsubscribe_from_games():
    leave_room(FIND_GAME_ROOM_KEY)
