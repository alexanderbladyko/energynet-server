from flask_socketio import join_room, emit
from flask_login import current_user

from auth.helpers import authenticated_only
from games.models import User, Game, Lobby
from utils.redis import redis


@authenticated_only
def join_lobby(data):
    id = data['id']

    user = User.get_by_id(current_user.id)

    if user.current_lobby_id or user.current_game_id:
        emit('new', {
            'success': False,
            'message': 'User is already in the game'
        })
        return

    lobby_exists = Lobby.contains(id)

    if not lobby_exists:
        emit('new', {
            'success': False,
            'message': 'No such game'
        })
        return

    game = Game.get_by_id(id, [Game.user_ids])

    pipeline = redis.pipeline()

    game.add_user(id, pipeline)
    game.save(p=pipeline)

    user.current_lobby_id = id
    user.save(p=pipeline)

    pipeline.execute()

    room_key = 'games:%s' % id
    join_room(room_key)

    emit('join_game', {
        'success': True,
    })
