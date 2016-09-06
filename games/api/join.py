from flask_socketio import join_room, emit
from flask_login import current_user

from auth.helpers import authenticated_only
from core.models import User, Game, Lobby
from utils.redis import redis_session
from utils.server import app


@authenticated_only
def join_lobby(data):
    app.logger.info(
        'Join lobby'
    )
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

    with redis_session() as pipeline:
        game.add_user(user.id)
        game.save(p=pipeline)

        user.current_lobby_id = id
        user.save(p=pipeline)

    room_key = 'games:%s' % id
    join_room(room_key)

    emit('join_game', {
        'success': True,
    })
