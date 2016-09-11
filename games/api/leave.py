from flask_socketio import leave_room, emit
from flask_login import current_user

from auth.helpers import authenticated_only
from core.models import User, Game
from games.logic import notify_lobby_users
from utils.redis import redis_session
from utils.server import app


@authenticated_only
def leave_lobby(data):
    app.logger.info('Leaving lobby')
    user = User.get_by_id(current_user.id, [User.current_lobby_id])

    if not user.current_lobby_id:
        emit('leave_game', {
            'success': False,
            'message': 'User is not in the lobby'
        })
        return

    game = Game.get_by_id(user.current_lobby_id, [Game.user_ids, Game.data])

    with redis_session() as pipeline:
        game.remove_user(user.id)
        game.save(p=pipeline)

        user.current_lobby_id = None
        user.save(p=pipeline)

    room_key = 'games:%s' % id
    leave_room(room_key)

    emit('leave_game', {
        'success': True,
    })
    notify_lobby_users(game=game)
